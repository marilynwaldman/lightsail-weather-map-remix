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
    k = 0
    for w in weather_df['PROD_TYPE'].unique():
        wxwarnings[w]=k
    #    print(w,k)
        k += 10

    
    all_values = wxwarnings.values()
    max_wxwarnings = max(all_values)
    min_wxwarnings = min(all_values)


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
    


def make_weather_map(weather_df, map_path, map_dir, vars):
    print("in make weather map")
    print(weather_df.head(2))
    print(map_path)
    print(map_dir)
    # weather_df - shape files with weather warnings
    # map_path - path to file with generated weather map, ie .html file

    # get the current time in UTC (constant reference timezone)
    
    # Use branca.colormap instead of choropleth
    # augment df with color features
    weather_df, max_wxwarnings, min_wxwarnings = crunch_data(weather_df)

    mbr = fl.Map(location=[40.0,-95.0],zoom_start=4,tiles="Stamen Toner")

    colormap = cm.linear.Set1_09.scale(min_wxwarnings,max_wxwarnings).to_step(len(set(weather_df['PROD_ID'])))
    print("after colormap")

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
                   fields=['PROD_TYPE','ISSUANCE','EXPIRATION'], 
                   aliases=['Hazard', 'Starts','Expires'],
                   labels=True,
                   localize=True
               ),
              ).add_to(mbr)

    # Add minimap
    MiniMap(tile_layer='stamenterrain',zoom_level_offset=-5).add_to(mbr)
    print("after map title")
    html_string = mbr.get_root().render()
    #vars['map_html'] = html_string
    return html_string

    if os.path.exists(map_dir) and os.path.isdir(map_dir):
        print("weathermaps directory exits")
        if os.path.exists(map_path):
            print("if map_path exits")
            os.remove(map_path)
            mbr.save(map_path) 
        if not os.path.exists(map_path):
            print("map does not exist yet- just save it") 
            mbr.save(map_path)
        print("map saved in if")
        return timestamp 
    else:
        print("map directory does not exist") 
        return None    
    
    




