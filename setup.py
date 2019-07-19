#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for nb_version_control"""

from __future__ import print_function
from setuptools import find_packages, setup

setup(
    name='snapbot',
    description="Version control, experiment tracking, script exporting, etc. for Jupyter notebooks",
    long_description="",
    version='0.0.1a1dev02',
    author='Sirong Huang',
    author_email='sirong.huang@selko.io',
    url=('https://github.com/selko-io/jupyter-toolbox'),
    keywords=['IPython', 'Jupyter', 'notebook','version control','experiment tracking','script export'],
    license='BSD-2-Clause',
    platforms=['Any'],
    packages=['snapbot'],
    include_package_data=True,
    data_files=[
        # like `jupyter nbextension install --sys-prefix`
        ("share/jupyter/nbextensions/snapbot", [
            "snapbot/static/index.js",
        ]),
        ("share/jupyter/nbextensions/snapbot", [
            "snapbot/static/handlers.js",
        ]),
        # like `jupyter nbextension enable --sys-prefix`
        ("etc/jupyter/nbconfig/notebook.d", [
            "jupyter-config/nbconfig/notebook.d/snapbot.json"
        ]),
        # like `jupyter serverextension enable --sys-prefix`
        ("etc/jupyter/jupyter_notebook_config.d", [
            "jupyter-config/jupyter_notebook_config.d/snapbot.json"
        ])
    ],
    install_requires=[
        'notebook >=4.0',
        'tornado'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
