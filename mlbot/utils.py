from datetime import datetime
import glob
import re
import json
import fastai
import sys
import mlflow
# make sure python version is >= 3.6
if sys.version_info[0] == 3 and sys.version_info[1] >= 6:
    from fastai.callbacks import LearnerCallback
else:
    class LearnerCallback:
        pass
    LearnerCallback.__module__ = 'fastai.callbacks'

#======================== Fastai Utils ========================#
class FastaiMLflowMonitor(LearnerCallback):
    """Logs train & validation loss and metrics """
    def __init__(self, experiment_id=None, runname=None, run_id=None, nested=False):
        self.experiment_id = experiment_id
        self.run_id = run_id
        self.runname = runname
        self.nested = nested
        
    def on_epoch_end(self, **kwargs):
        mlflow.log_metric('train_loss', float(kwargs['smooth_loss']))
        metric_values = kwargs['last_metrics']
        metric_names = ['val_loss'] + kwargs['metrics']
        for metric_value, metric_name in zip(metric_values, metric_names):
            metric_name = getattr(metric_name, '__name__', metric_name)
            mlflow.log_metric(str(metric_name), float(metric_value))

    def on_batch_end(self, **kwargs):
        mlflow.log_metric('train_batch_loss', float(kwargs['last_loss']))


fastai_learners = ['Learner', 'language_model_learner', 'text_classifier_learner', 
                    'RNNLearner', 'LanguageLearner', 'TabularModel', 'CollabLearner',
                    'cnn_learner', 'unet_learner', 'GANLearner']

def is_block(log_name, cell):
    """Returns True for non-empty notebook code block that contains #log_name"""
    if cell['cell_type'] != 'code': return False
    src = cell['source']
    if len(src) == 0 or len(src[0]) < len(log_name)+1: return False
    # there could be: any number of whitespace char in between # and log_name, 
    # log_name can be followed with any character, eg. s
    flag = re.match(fr'^\s*#\s*{log_name}.*\s*$', src[0], re.IGNORECASE) is not None
    return flag

def block_contains(pattern, cell):
    """Returns True for non-empty notebook code block that contains pattern"""
    if cell['cell_type'] != 'code': return False
    src = cell['source']
    if len(src) == 0 : return False
    check_all = [re.search(f'^.*{pattern}.*$', line, re.IGNORECASE) for line in src]
    if all(check is None for check in check_all):
        return False
    else: 
        return True

def remove_by_idxs(ls, idxs):
    """Remove list of indexes from a target list at the same time"""
    return [i for j, i in enumerate(ls) if j not in idxs]

#======================== Time Utils ========================#

def datetime_to_str(dt):
    """
    Convert default datetime format to str & remove digits after int part of seconds
    """
    result = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-7]
    return result


def last_modified_time(filename):
    #! not in use currently
    """
    Calculates the time when the file is last modified
    """
    t = os.path.getmtime(filename)
    # convert to datetime
    dt = datetime.fromtimestamp(t)
    return datetime_to_str(dt)


def time_until_now(strtime):
    #! not in use currently
    """
    Calculates how many months/d/h/m/s ago between given string datetime and now
    """
    def date_diff_in_seconds(dt2, dt1):
        diff = dt2 - dt1
        return diff.days * 24 * 3600 + diff.seconds

    def dhms_from_seconds(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        months, days = divmod(days, 30)
        return (months, days, hours, minutes, seconds)

    date1 = datetime.strptime(strtime, '%Y-%m-%d %H:%M:%S')
    date2 = datetime.now()
    diff = dhms_from_seconds(date_diff_in_seconds(date2, date1))
    labels = ['months', 'd', 'h', 'm', 's']
    for i, _t in enumerate(diff):
        if _t > 0:
            label = f'{diff[i]} {labels[i]} ago'
            if i<=3:
                label = f'{diff[i+1]} {labels[i+1]} ago '
            else:
                label = f'{diff[i]} {labels[i]} ago'
        else:
            label = 'just now'
        break
    return label


#======================== Other Utils ========================#


def index_versions():
    #! Outdated, not in use currently
    """
    Search through custom local directory for historical versions and their info
    """
    fnames = glob.glob(version_dir+"*/*.ipynb", recursive=True)
    versions = [v.split('/')[-2] for v in fnames]

    tmp = []
    for f, v in zip(fnames, versions):
        time = last_modified_time(f)
        time_until_now = time_until_now(time)
        tmp.append(dict(fname=f, version=v, time=time,
                        time_until_now=time_until_now))
    tmp = sorted(tmp, key=lambda t: t['version'], reverse=True)

    with open(version_dir+'version_log.json', 'w') as fout:
        json.dump(tmp, fout)
