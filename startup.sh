#!/bin/bash

# create virtual environment
python3 -m venv myenv
source myenv/bin/activate

# install required packages
pip install -r requirements.txt

# run django migrations
python3 manage.py migrate
