# Imports

from ctypes import addressof
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
pharmacies = pd.read_csv('pharmacies_map.csv', sep=';')

print('Enter user address:')
user = input()
print('How many options do you need?')
options = input()
# Map

Santiago = folium.Map(location = [-33.447487, -70.673676], zoom_start = 10)


# Distance function

def euclid_std(point_from, point_to, standard_deviations):
    return sum(((point_from - point_to) / standard_deviations) ** 2) ** 0.5


def euclid_diag(point_from, point_to, standard_deviations):
    return euclid_std(point_from, point_to, standard_deviations) \
           * (np.prod(standard_deviations ** 2)) ** (1. / point_from.shape[0])


# Get user function

def get_user(user):

    geolocator = Nominatim(user_agent="data_care")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    user_code = geolocator.geocode(user)
    user_lat = user_code.latitude
    user_lon = user_code.longitude

    return folium.Marker([user_lat, user_lon], popup='You', icon=folium.Icon(color='red')).add_to(Santiago), user_lat, user_lon

get_user(user)

# Get closest function

def get_closest_pharmacies(int):
    distances = []
    
    Latitudes = list(pharmacies.Latitude)
    Longitudes = list(pharmacies.Longitude)
    
    for lat, lon in zip(Latitudes,Longitudes):
        distances.append(euclid_diag(np.array([lat,lon]), np.array([user_lat,user_lon]), 0.5))
    
    pharmacies['Distances'] = distances
    closest_pharmacies = pharmacies[['Nombre Local','Address']].sort_values(by='Distances')[:int]

    close_lat = list(closest_pharmacies.Latitude)
    close_lon = list(closest_pharmacies.Longitude)

    for lat, lon in zip(close_lat,close_lon):
        folium.Marker([lat,lon]).add_to(Santiago)   
    
    return closest_pharmacies


# Input
get_closest_pharmacies(options)

# Display

Santiago