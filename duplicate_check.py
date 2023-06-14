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

