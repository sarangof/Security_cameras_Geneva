import requests
import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import plotly.express as px
import folium
import numpy as np

# overpass_url = "http://overpass-api.de/api/interpreter"
# overpass_query = """
# [out:json];
# area["ISO3166-1"="CH"][admin_level=2];
# (node["man_made"="surveillance"](area);
#  way["man_made"="surveillance"](area);
#  rel["man_made"="surveillance"](area);
# );
# out center;
# """
# response = requests.get(overpass_url, 
#                         params={'data': overpass_query})
                        
# data = response.json()
# # Writing to sample.json

# data['elements']   
# json_object = json.dumps(data['elements'], indent=4)
# with open("sample.json", "w") as outfile:
#     outfile.write(json_object)

geodf_boundaries = gpd.read_file('./data/CHE_adm0.shp')

cameras_CH = pd.read_json('./sample.json')

geometry = [Point(xy) for xy in zip(cameras_CH.lon, cameras_CH.lat)]
cameras_CH = cameras_CH.drop(['lon', 'lat'], axis=1)
gdf = gpd.GeoDataFrame(cameras_CH, crs="EPSG:4326", geometry=geometry)
# Get centroids 
points = gdf.to_crs("EPSG:4326").geometry.centroid
# Define new columns 
gdf['lat'] = points.apply(lambda x : x.y if x else np.nan)
gdf['lon'] = points.apply(lambda x : x.x if x else np.nan)
df_to_plot = pd.DataFrame(gdf.drop(columns='geometry'))
fig = px.scatter_mapbox(df_to_plot,lon='lon',lat='lat',hover_name='id',zoom=5.8,color_discrete_sequence=["goldenrod"])
fig.update_layout(mapbox_style="carto-darkmatter",
                  mapbox={
                            "layers": [
                                        {
                                            "source": geodf_boundaries["geometry"].__geo_interface__,
                                            "type": "line",
                                            "color": "red"
                                            }
                                        ]
                            }
                    )
fig.show()
fig.write_html("surveillance_cameras_CH.html")

username = '' # your username
api_key = '' # your api key - go to profile > settings > regenerate key
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)