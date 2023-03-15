# Package imports
import requests
import json
import geopandas as gpd 
import pandas as pd
from shapely.geometry import Point
import plotly.express as px
import folium
import numpy as np
import chart_studio
import chart_studio.plotly as py

# Function definitions
def flatten_data(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# OSM overpass API query
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
area["name"="Genève"][admin_level=4];
(node["man_made"="surveillance"](area);
 way["man_made"="surveillance"](area);
 rel["man_made"="surveillance"](area);
);
out center;
""" #area["ISO3166-1"="CH"][admin_level=2]; area["name"="Genève"]["boundary"="administrative"]
response = requests.get(overpass_url, params={'data': overpass_query})

# Run program if things hold (gotta change this to the pythonic way)
if str(response)=='<Response [200]>':                        
    # Structure response
    foo = response.json()
    print(foo['elements'])
    cameras_GE = pd.DataFrame([flatten_data(x) for x in foo['elements']])

    #Read geographic files
    switzerland_boundaries = gpd.read_file('./data/CHE_adm0.shp')
    geneva_canton_boundaries = gpd.read_file('./Canton Geneva/CantonGeneva_merged.shp').to_crs(crs="EPSG:4326")
    geneva_city_boundaries = gpd.read_file('./Geneva City/Ville_de_Genève.shp').to_crs(crs="EPSG:4326")
    
    geometry = [Point(xy) for xy in zip(cameras_GE.lon, cameras_GE.lat)]
    cameras_GE = cameras_GE.drop(['lon', 'lat'], axis=1)
    gdf = gpd.GeoDataFrame(cameras_GE, crs="EPSG:4326", geometry=geometry)
    # Get centroids 
    points = gdf.to_crs("EPSG:4326").geometry.centroid
    # Define new columns 
    gdf['lat'] = points.apply(lambda x : x.y if x else np.nan)
    gdf['lon'] = points.apply(lambda x : x.x if x else np.nan)
    df_to_plot = pd.DataFrame(gdf.drop(columns='geometry'))
    fig = px.scatter_mapbox(df_to_plot,lon='lon',lat='lat',hover_name='id',zoom=9,color_discrete_sequence=["goldenrod"])
    fig.update_layout(mapbox_style="carto-darkmatter",
                    mapbox={
                                "layers": [
                                            {
                                               "source": geneva_canton_boundaries["geometry"].__geo_interface__,
                                               "type": "line",
                                               "color": "blue"
                                               },
                                            {
                                                "source": geneva_city_boundaries["geometry"].__geo_interface__,
                                                "type": "line",
                                                "color": "red"
                                                }
                                            ]
                                }
                        )
    fig.show()
    fig.write_html("surveillance_cameras_GE.html")

    username = '' # your username
    api_key = '' # your api key - go to profile > settings > regenerate key
    chart_studio.tools.set_credentials_file(username=username, api_key=api_key)
    py.plot(fig, filename = 'CH_surveillance_cameras', auto_open=True)

# Do not think I need this; not sure.
#cameras_GE = pd.read_json('./sample.json')
''' 
json_object = json.dumps(foo['elements'], indent=4)
with open("sample.json", "w") as outfile:
    outfile.write(json_object)
'''