# Program wxwarning
# by Todd Arbetter (todd.e.arbetter@gmail.com)
# Software Engineer, IXMap, Golden, CO

# collects latests National Weather Service Warnings, Watches, Advisories,
# and Statements, plots shapefiles on an interactive map in various colors.
# The map is able to pan and zoom, and on mouseover will give the type of
# weather statement, start, and expiry.


import requests
#from flask import Flask, jsonify
import time
import tarfile
import os as os
import urllib3
import shutil
from pathlib import Path
import geopandas as gpd
import pandas as pd

def awaitdata(destination):
    for i in range (0,10):
         if  os.path.exists(destination): 
             return  tarfile.open(name=destination)

         time.sleep(1)
    return None


def get_weather_data(app):
    # We create a downloads directory within the streamlit static asset directory
    # and we write output files to it

    #get latest wx warnings from NWS

     url='https://tgftp.nws.noaa.gov/SL.us008001/DF.sha/DC.cap/DS.WWA/current_all.tar.gz'
     cwd = Path.cwd()
     
    
     dest_path = os.path.join(os.getcwd(), 'downloads/')
     
     if os.path.exists(dest_path) and os.path.isdir(dest_path):
         shutil.rmtree(dest_path)

     os.mkdir(dest_path) 
     destination =  str(dest_path)+'current_all.tar.gz'

     http = urllib3.PoolManager()
     try:
         resp = http.request(
             "GET",
              url,
              preload_content=False)
         with open(destination,"wb") as f:
             for chunk in resp.stream(32):
                f.write(chunk)

         resp.release_conn() 
         wxdata = awaitdata(destination)
         if wxdata == None:
             return None

         wxdata.list(verbose=True)
         wxdata.extractall(path=str(dest_path)+'/current_all/')
         infile = str(dest_path) + '/current_all/current_all.shp'
         
         if os.path.exists(infile):
              weather_df = gpd.read_file(infile)    
              weather_df = weather_df.drop(columns=['PHENOM','SIG','WFO','EVENT','CAP_ID','MSG_TYPE','VTEC'])  
              return weather_df
         else:
              return None     

     except Exception as e:
       return None

  



