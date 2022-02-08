import geopandas as gpd
import pandas as pd
import numpy as np
import json
import geojson
import h3
import folium
import osmnx as ox
from shapely import wkt
from folium.plugins import HeatMap
from shapely.geometry import Polygon
import requests
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import matplotlib.pyplot as plt
import os
import sys

user = sys.argv[0]

Santiago = folium.Map(location = [-33.447487, -70.673676], zoom_start = 13)

geolocator = Nominatim(user_agent="my_request")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

user = user.apply(geocode)
lat = user.apply(lambda x: x.latitude if x else None)
lon = user.apply(lambda x: x.longitude if x else None)

folium.Marker([lat,lon]).add_to(Santiago)
Santiago
