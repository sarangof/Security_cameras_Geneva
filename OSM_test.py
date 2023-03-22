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
def get_baseline_ids():
    baseline_ids_list = []
    with open(r'./baseline_ids_list_16-03-2023.txt', 'r') as fp:
        for line in fp:
            x = line[:-1]
            baseline_ids_list.append(int(x))
    return baseline_ids_list
def update_table_based_on_new_ids(df,baseline_ids_list):
    df.loc[df["id"].isin(baseline_ids_list), "New"] = 'Security cameras'
    df.loc[~df["id"].isin(baseline_ids_list), "New"] = 'New security cameras logged'
    return df

#Loads
hover_names = {"type":False,"id":True,"Type of mount":True,"Type of camera":True,"tags_ele":False,"tags_man_made":False,"Location":True,"tags_surveillance:type":False,"tags_surveillance:zone":False,"tags_camera:direction":False,"tags_addr:city":False,"tags_addr:housenumber":False,"tags_addr:street":False,"tags_direction":False,"tags_camera:count":False,"tags_manufacturer":False,"lat":False,"lon":False,"Image URL":True,"New":False}
baseline_ids_list = get_baseline_ids()

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
    """ 
response = requests.get(overpass_url, params={'data': overpass_query})


# Run program if things hold (gotta change this to the pythonic way)
if str(response)=='<Response [200]>':                        
    # Structure response
    foo = response.json()
    print(foo['elements'])
    cameras_GE = pd.DataFrame([flatten_data(x) for x in foo['elements']])

    #Read geographic files
    #switzerland_boundaries = gpd.read_file('./Switzerland/CHE_adm0.shp')
    geneva_canton_boundaries = gpd.read_file('./Canton Geneva/CantonGeneva_merged.shp').to_crs(crs="EPSG:4326")
    #geneva_city_boundaries = gpd.read_file('./Geneva City/Ville_de_Genève.shp').to_crs(crs="EPSG:4326")
    
    # Convert to geodataframe
    geometry = [Point(xy) for xy in zip(cameras_GE.lon, cameras_GE.lat)]
    cameras_GE = cameras_GE.drop(['lon', 'lat'], axis=1)
    gdf = gpd.GeoDataFrame(cameras_GE, crs="EPSG:4326", geometry=geometry)
    points = gdf.to_crs("EPSG:4326").geometry.centroid
    gdf['lat'] = points.apply(lambda x : x.y if x else np.nan)
    gdf['lon'] = points.apply(lambda x : x.x if x else np.nan)

    #Plot
    df_to_plot = pd.DataFrame(gdf.drop(columns='geometry')).replace({'node':'Security camera'})
    df_to_plot = update_table_based_on_new_ids(df_to_plot,baseline_ids_list).rename(columns={'tags_camera:mount':"Type of mount",'tags_camera:type':"Type of camera",'tags_surveillance':"Location",'tags_image':"Image URL"})
    fig = px.scatter_mapbox(
                            df_to_plot,
                            lon='lon',
                            lat='lat',
                            hover_data=hover_names,
                            zoom=9.5,
                            color='New',
                            color_discrete_sequence=["goldenrod","white"],
                            labels={'type':' '},
                            title='Security cameras in Geneva'
                            )
    fig.update_layout(
                        mapbox_style="carto-darkmatter",
                        mapbox={
                                "layers": [
                                            {
                                               "source": geneva_canton_boundaries["geometry"].__geo_interface__,
                                               "type": "line",
                                               "color": "red"
                                               } 
                                            ]
                                },
                        showlegend=True,
                        title=dict(
                                    x=0.065,
                                    y=0.89,
                                    font=dict(
                                                family="Georama",
                                                size=26,
                                                color="Black"
                                            ),
                        ),
                        legend=dict(
                                        borderwidth=2,
                                        itemclick= 'toggleothers',# when you are clicking an item in legend all that are not in the same group are hidden
                                        x=0.75,
                                        y=0.05,
                                        traceorder="reversed",
                                        title_font_family="Georama",
                                        title_font_size=1,
                                        font=dict(
                                            family="Georama",
                                            size=13,
                                            color="white"
                                            ),
                                        bgcolor="rgb(0,128,128)",
                                        bordercolor="rgb(0,128,128)"
                                        ),
                            hoverlabel=dict(
                                            bgcolor="rgb(0,128,128)",
                                            bordercolor="rgb(0,128,128)",
                                            font_color="white",
                                            font_size=10,
                                            font_family="Georama"
                                            )   
                            )
    config_param = {
        #'frameMargins':0,
        'fillFrame':False,
        'responsive':True,
        'autosizable':True
    }
    fig.show()
    fig.write_html("index.html",full_html=False,config=config_param),
else:
    pass

# Do not think I need this; not sure.
#cameras_GE = pd.read_json('./sample.json')
''' 
json_object = json.dumps(foo['elements'], indent=4)
with open("sample.json", "w") as outfile:
    outfile.write(json_object)



                                            {
                                                "source": geneva_city_boundaries["geometry"].__geo_interface__,
                                                "type": "line",
                                                "color": "red"
                                                }

'''

""" 
   path = 'https://github.com/sarangof/Security_cameras_Geneva/blob/main/Canton%20Geneva.zip!CantonGeneva_merged.shp'
    geneva_canton_boundaries = gpd.read_file(path).to_crs(crs="EPSG:4326")
    # 
    #area["ISO3166-1"="CH"][admin_level=2]; area["name"="Genève"]["boundary"="administrative"]"""