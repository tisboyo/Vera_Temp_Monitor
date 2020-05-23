#!/bin/bash

git -C /usr/src/app/Vera_Temp_Monitor pull

python -m pip install -U -r /usr/src/app/Vera_Temp_Monitor/requirements.txt

python /usr/src/app/Vera_Temp_Monitor/main.py

