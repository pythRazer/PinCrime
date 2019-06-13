import pandas
import json
from geopy.geocoders import ArcGIS
import folium
import numpy

crime_color = {
    'anti-social-behaviour': 'red',
    'bicycle-theft': 'blue',
    'burglary': 'green',
    'criminal-damage-arson': 'purple',
    'drugs': 'orange',
    'other-theft': 'darkred',
    'possession-of-weapons': 'lightred',
    'public-order': 'beige',
    'robbery': 'darkblue',
    'shoplifting': 'darkgreen',
    'theft-from-the-person': 'cadetblue',
    'vehicle-crime': 'darkpurple',
    'violent-crime': 'pink',
    'other-crime': 'yellow'
}


def request(lat, lon):
    df1_request = "https://data.police.uk/api/crimes-street/all-crime?lat=" + lat + "&" + "lng=" + lon
    df1 = pandas.read_json(df1_request)
    lanlon(df1)


def lanlon(df):
    for i in range(df["location"].size):
        lat = float(df["location"].get(i)["latitude"])
        lon = float(df["location"].get(i)["longitude"])

        ctg = df["category"][i]

        marking(lat, lon, ctg)

        # print(str(i) + ": " + str(lat) + ", " + str(lon))


fg = folium.FeatureGroup(name="Crime Map")


def marking(lt, ln, ctg):

    if ctg not in crime_color.keys():
        ctg = 'other-crime'

    fg.add_child(
        folium.Marker(location=[lt, ln],
                      popup=ctg,
                      icon=folium.Icon(color=crime_color[ctg])))


user_lat = "51.509865"
user_lon = "-0.118092"

request(user_lat, user_lon)

map = folium.Map(location=[user_lat, user_lon],
                 zoom_start=20,
                 titles="Crime Map")
map.add_child(fg)
map.save("ByeByeCrime.html")
