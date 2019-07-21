from datetime import datetime
import glob
import json

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
