#!/bin/bash
virtualenv -p python3.7 .env
source .env/bin/activate
pip install -r requirements.txt
source .env/bin/activate

