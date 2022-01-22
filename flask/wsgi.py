# Create running instance of weather map app

import os as os
import pathlib
import zipfile
import json
from functools import wraps, update_wrapper
from datetime import datetime
from pathlib import Path
from weather_data import  get_weather_data
from weather_map import make_weather_map 
import shutil


from app import server

if __name__ == "__main__":

    server.run(host='0.0.0.0', port=8000)