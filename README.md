# MLbot - Jupyter notebook version control, experiment tracking

![](demos/demo1.gif)


## Installation
`pip intall mlbot`

The project is under constant development of alpha version. `pip install --upgrade mlbot` to upgrade to newest version.

> #### Important
> After installation/upgrade, restart jupyter notebook instace (restart cloud instance if using one) for the changes to take effect. 

## Features

1. Version control
    - multiple storage options
    - show historical versions in dropdown menu
    - switch to specific version of the notebook with a click

2. Automatically experiment tracking
    - parameters, loss, metrics, data version, model etc....
    - using MLFlow at the moment: 
        - by default logging locally to current working directory
        - if MLFLOW_TRACKING_URI and AWS credentials are set up, logging to remote server
        
## Todo:
- save to github
- save to gitlab

## Limitations:
- when the notebook is renamed, it'll generate a new save folder for the newly named notebook without access to previous versions. Can be possibly solved by creating custom ContentManager API.
- MLFlow automatic experiment tracking only works with fastai at the moment. Support for other languages coming later.
