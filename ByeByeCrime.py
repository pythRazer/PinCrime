import pandas
import json
from geopy.geocoders import ArcGIS
import folium
import sys
import urllib
import os
import numpy



while True:


    input_method = input("Address for 1, latitude and longitude for 2, close the app for 3: ")

    if(input_method == "1"):
        try:
            user_address = input("Please enter the address: ")
            geolocator = ArcGIS(user_agent="ByeByeCrime")
            location = geolocator.geocode("UK" + user_address)
            print(location.address)
            print(location.latitude, location.longitude)
            user_lat = str(location.latitude)
            user_lon = str(location.longitude)
        except:
            print("Invalid address, try again, or input the latitude and longitude instead")
            continue
        else:
            break
    elif(input_method == "2"):
        try:
            user_lat = input("Please enter the latitude: ")
            user_lon = input("Please enter the longitude: ")
            if(user_lat.isdigit() != True or user_lon.isdigit() != True):
                print("Invalid latitude or longitude, please try again lll")
                continue
        except:
            print("Invalid latitude or longitude, please try again")
            continue
        else:
            break

    elif(input_method == "3"):
        print("Closed")
        sys.exit()

    else:
        print("Invalid input, please try again")
        continue




    # if(input_method != "1" or input_method != "2"):
    #     print("Invalid input, please try again")
    #     continue



print("Processing...")

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
    'other-crime': 'white'
}


def request(lat, lon):
    df1_request = "https://data.police.uk/api/crimes-street/all-crime?lat=" + str(lat) + "&" + "lng=" + str(lon)
    try:
        df1 = pandas.read_json(df1_request)
    except:
        print("")

    print(df1["location"].size)
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


request(user_lat, user_lon)

map = folium.Map(location=[user_lat, user_lon],
                 zoom_start=20,
                 titles="Crime Map")
map.add_child(fg)

map.save("ByeByeCrime.html")
# path = os.path.abspath("ByeByeCrime.html")
# page = urllib.request.urlopen(path).read()
# print(page)
# html_string = map.get_root().render()
# f = codecs.open("ByeByeCrime.html", "r", "utf-8")
print("The map was generated successfully")
#36.84183000000007 -76.05180999999999
#51.503659988314624 -0.11925004443394603


