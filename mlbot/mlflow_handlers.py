import os
import re
import shutil
import json
import numpy as np
import mlflow
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from datetime import datetime
from .utils import datetime_to_str, is_block, FastaiMLflowMonitor, block_contains, fastai_learners, remove_by_idxs
from notebook.base.handlers import IPythonHandler


class MLflowExperimentHandler(IPythonHandler):
    """
    Create an MLflow experiment which logs:
    - convert notebook blocks that start with: #hyperparameter, #input and #output to appropriate mlflow logs
    - logs notebook checkpoint after execution with execution outputs displayed in notebook
    - logs train/val loss and metrics automatically #!currently only supports fastai
    """

    def get(self):
        """
            - adds tracking uri + start run
            - adds tracking code for hyperparameters, input, output, loss, metrics
            => save the new modified notebook as a temporary file and execute it notebook and save it and upload it
            - end run / end run normally and log source notebook to the right run id
        """

        # get needed paths
        root = os.getcwd()                                      # /Users/rongmac
        current_fpath = self.get_query_argument('fpath')        # './ML/cat-dog/classifier.ipynb'
        current_dir = ''.join(
            [p+'/' for p in current_fpath.split('/')[:-1]])     # './ML/cat-dog/'
        fname = current_fpath.split("/")[-1]                    #'classifier.ipynb'
        absolute_current_dir = root + current_dir[1:]

        # get code blocks with specific tags
        notebook = json.load(open(current_fpath, 'r', encoding="utf-8"))
        hyperparameters = [c for c in notebook['cells']
                           if is_block('hyperparameter', c)]
        inputs = [c for c in notebook['cells'] if is_block('input', c)]
        outputs = [c for c in notebook['cells'] if is_block('output', c)]
        models = [c for c in notebook['cells'] if any(
            [block_contains(pattern, c) for pattern in fastai_learners])]

        # add starting mlflow run block
        #! user must set environment variable otherwise use default local mlflow
        #! no need to print anything here... change it to somewhere else
        start = ['import mlflow\n',
                 'import os\n',
                 'from mlbot.utils import FastaiMLflowMonitor\n'
                 "MLFLOW_TRACKING_URI = os.environ['MLFLOW_TRACKING_URI']\n",
                 "if MLFLOW_TRACKING_URI is not None: url = MLFLOW_TRACKING_URI.split('@')[-1]\n",
                 "if MLFLOW_TRACKING_URI is not None: print(f'Logging experiment to http://{url}')\n",
                 "else: print('Run `mlflow ui` in current working directory to start server'); print('Logging experiment locally to http://localhost:5000/#/')\n",
                 "mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)\n",
                 "mlflow.start_run(experiment_id=0, run_name = None)\n", #! change this to user specified!!!
                 "run_id = mlflow.active_run().info.run_id\n"
                 ] 
        
        start_block = {'cell_type': 'code',
                       'execution_count': 0,
                       'metadata': {},
                       'outputs': [],
                       'source': start}
        notebook['cells'].insert(0, start_block)

        id_block = {'cell_type': 'code',
                    'execution_count': 0,
                    'metadata': {},
                    'outputs': [],
                    'source': ['print(run_id)']}
        notebook['cells'].insert(1, id_block)

        idxs = []
        idxs.append(0)
        idxs.append(1)

        # log hyperparameters
        for block in hyperparameters:
            idx = notebook['cells'].index(block) + 1
            idxs.append(idx)
            log = []
            for line in block['source']:
                if re.search(r'\=', line) is not None:
                    line = line.replace('\n', '').replace(' ', '')
                    key = line.split('=')[0]
                    value = line.split('=')[-1]
                    log.append(f"mlflow.log_param('{key}', {value})" + "\n")
            log_block = {'cell_type': 'code',
                        'execution_count': 0,
                        'metadata': {},
                        'outputs': [],
                        'source': log}

            notebook['cells'].insert(idx, log_block)

        # add callback to log loss + metrics
        for block in models:
            src = block['source']
            for line in src:
                if any([re.search(fr'=.*{pattern}\(',line) is not None for pattern in fastai_learners]):
                    line_idx = src.index(line) +1
                    model = line.split('=')[0].strip()
                    break
            log = f"{model}.callbacks.append(FastaiMLflowMonitor())\n" 
            src.insert(line_idx, log)

        end_block = {'cell_type': 'code', 
                    'execution_count': 0, 
                    'metadata': {}, 
                    'outputs': [], 
                    'source': ["mlflow.end_run()"]}
        # insert a block that logs all filepaths at the end of notebook
        notebook['cells'].append(end_block)
        idxs.append(len(notebook['cells'])-1)

        # write the temporary notebook with mlflow logging codes and 
        # list of indexes of those logging cells to files
        tmp_notebook_fname = current_dir+'tmp-'+fname
        with open(tmp_notebook_fname, 'w') as fout:
            json.dump(notebook, fout)

        # execute the temporary notebook, remove logging cells, log to mlflow
        execution_fname = current_dir+'executed-'+fname 
        with open(tmp_notebook_fname) as f:
            nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': current_dir}})
        run_id = nb['cells'][1]['outputs'][-1]['text'].replace('\n','')
        #artifact_folder = 's3://selko-mlflow/0/'+run_id+'/artifacts/'
        with open(execution_fname, 'w', encoding='utf-8') as fin:
            nb['cells'] = remove_by_idxs(nb['cells'], idxs)
            nbformat.write(nb, fin)
        os.remove(tmp_notebook_fname)

        # log the source code notebook with execution outputs
        if os.environ['MLFLOW_TRACKING_URI'] is not None:
            mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
        else:
            mlflow.set_tracking_uri('')
        mlflow.start_run(experiment_id=0, run_id=run_id) #! Todo: make it user definable  ! hard-coded exp_id
        
        # get all the valid file paths from input and output blocks, log as artifacts
        fpaths = []
        for block in inputs+outputs:
            idx = notebook['cells'].index(block) +1
            for line in block['source']:
                # get the potential filepath strings 
                pattern = re.search(r"'.*'", line)
                if pattern:
                    path = line[re.search(r"'.*'", line).start()+1:re.search(r"'.*'", line).end()-1]   
                    if os.path.isfile(absolute_current_dir+path):
                        fpaths.append(absolute_current_dir+path)
                    elif os.path.isfile(absolute_current_dir+path+'.pth'):
                        fpaths.append(absolute_current_dir+path+'.pth')
                    elif os.path.isfile(absolute_current_dir+'models/'+path+'.pth'):
                        fpaths.append(absolute_current_dir+'models/'+path+'.pth')
        for p in fpaths:
            mlflow.log_artifact(p) 
        mlflow.log_artifact(execution_fname)
        mlflow.end_run()

       #! Todo: log experiment info and notebook s3 url path into json and display it as a dropdown

