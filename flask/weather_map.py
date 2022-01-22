# Program wxwarning
# by Todd Arbetter (todd.e.arbetter@gmail.com)
# Software Engineer, IXMap, Golden, CO

# collects latests National Weather Service Warnings, Watches, Advisories,
# and Statements, plots shapefiles on an interactive map in various colors.
# The map is able to pan and zoom, and on mouseover will give the type of
# weather statement, start, and expiry.

import geopandas as gpd
import folium as fl
from folium.plugins import MiniMap
import branca.colormap as cm
import os as os
import datetime as dt

def crunch_data(weather_df):
    wxwarnings = {}
    k = 5
    for w in weather_df['PROD_TYPE'].unique():
        wxwarnings[w]=k
        k += 10

    
    all_values = wxwarnings.values()
    max_wxwarnings = max(all_values)+5
    min_wxwarnings = min(all_values)-5


    # Now create an column PROD_ID which duplicates PROD_TYPE
    weather_df["PROD_ID"]=weather_df['PROD_TYPE']

    # and fill with values from the dictionary wxwarnings
    weather_df['PROD_ID'].replace(wxwarnings,inplace=True)

    #st.write(weather_df.head())

    #verify no missing/Nan
    weather_df.isnull().sum().sum()

    #explicitly create an index column with each entry having a unique value for indexing
    weather_df['UNIQUE_ID']=weather_df.index

    return weather_df, max_wxwarnings, min_wxwarnings
    


def make_weather_map(weather_df, map_path, map_dir):
    
    # weather_df - shape files with weather warnings
    # map_path - path to file with generated weather map, ie .html file

    # get the current time in UTC (constant reference timezone)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes')
    
    # Use branca.colormap instead of choropleth
    # augment df with color features
    weather_df, max_wxwarnings, min_wxwarnings = crunch_data(weather_df)

    mbr = fl.Map(location=[40.0,-95.0],zoom_start=4,tiles="Stamen Toner")

    colormap = cm.linear.Set1_09.scale(min_wxwarnings,max_wxwarnings).to_step(len(set(weather_df['PROD_ID'])))
    

##### Merge (dissolve) weather data by warning type, onset, expiration

    weather_dfmerge = weather_df.dissolve(by=['PROD_TYPE','ONSET','ENDS'],aggfunc='first',as_index=False,dropna=False)
    weather_df = weather_dfmerge

    #Simplify geometry to reduce size of plot
    weather_df['geometry']=weather_df['geometry'].simplify(tolerance=0.01)

######

    #Add weather data to map with mouseover (this will take a few minutes), include tooltip

    fl.GeoJson(weather_df,
               style_function = lambda x: {"weight":0.5, 
                            'color':'red',
                            'fillColor':colormap(x['properties']['PROD_ID']), 
                            'fillOpacity':0.5
               },
           
               highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.25, 
                                'weight': 0.1
               },
               
               tooltip=fl.GeoJsonTooltip(
                   fields=['PROD_TYPE','ONSET','ENDS'], 
                   aliases=['Hazard', 'Starts','Expires'],
                   labels=True,
                   localize=True
               ),
              ).add_to(mbr)

    # Add minimap
    MiniMap(tile_layer='stamenterrain',zoom_level_offset=-5).add_to(mbr)
    
    if os.path.isdir(map_dir):
        
        if os.path.exists(map_path):
            os.remove(map_path)
            mbr.save(map_path) 
            return timestamp
        else:
            return None
    else:
        return None
    




