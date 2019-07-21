import os
import shutil
import json
from datetime import datetime
from .utils import datetime_to_str
from notebook.base.handlers import IPythonHandler

version_folder = 'nb_versions/'


class ChangeVersionHandler(IPythonHandler):
    """
    Copy over the selected version to the current working directory and overwrite
    """

    def get(self):
        # for locally saved versions
        version = self.get_query_argument('fpath')  
        current_dir = ''.join([p+'/' for p in version.split('/')[:-3]])
        fname = version.split("/")[-2]
        current_fpath = current_dir + fname + '.ipynb'
        shutil.copyfile(version, current_fpath)

        self.write('Copying over the selected version')


class SaveLocallyHandler(IPythonHandler):
    """ 
    Creates a folder in the notebook's cwd called 'nv_versions', 
    each notebook version is saved inside a subfolder of name 
    'v-{version number}', eg. 'v-1','v-2'.
    """

    def get(self):
        # get all the paths and fnames needed
        fpath = self.get_query_argument('fpath')
        current_dir = ''.join([p+'/' for p in fpath.split('/')[:-1]])
        version_dir = current_dir + version_folder
        note = self.get_query_argument('note')
        fname = fpath.split("/")[-1]
        fname_only = fname.split(".")[0]
        # create folders
        if not os.path.isdir(version_dir):
            os.makedirs(version_dir, exist_ok=True) 
        notebook_version_dir = version_dir+fname_only+'/'
        if not os.path.isdir(notebook_version_dir):
            os.makedirs(notebook_version_dir, exist_ok=True)

        # assign incremental version number
        i = 1
        while os.path.exists(notebook_version_dir+fname_only+f'-{i}.ipynb'):
            i += 1
        new_fpath = notebook_version_dir+fname_only+f'-{i}.ipynb'
        shutil.copyfile(fpath, new_fpath)
        time_now = datetime_to_str(datetime.now())

        # write json with version info and version notes
        notebook_info = dict(fpath=new_fpath, version=i, time=time_now, note=note)
        log_fpath = notebook_version_dir + 'version_log.json'
        if os.path.exists(log_fpath):
            with open(log_fpath, 'r') as fin:
                version_list = json.load(fin)['versions']
                version_list.append(notebook_info)
        else:
            version_list = [notebook_info]
        json_data = {'versions':version_list}
        with open(log_fpath, 'w') as fout:
            json.dump(json_data, fout)

        self.write('works')


        

