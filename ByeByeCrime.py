import pandas
from geopy.geocoders import ArcGIS
import folium
import sys
from urllib.request import urlopen
import json

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
    'vehicle-crime': 'gray',
    'violent-crime': 'pink',
    'other-crime': 'lightgreen'
}


def request(lat, lon):
    df1_request = "https://data.police.uk/api/crimes-street/all-crime?lat=" + str(lat) + "&" + "lng=" + str(lon)
    try:
        df1 = pandas.read_json(df1_request)
    except:
        print("Error")

    print("Number of crime: ", df1["location"].size)
    latlon(df1)


fg = folium.FeatureGroup(name="ByeByeCrime")


def latlon(df):
    print("Making the map...")
    for i in range(df["location"].size):
        lat = float(df["location"].get(i)["latitude"])
        lon = float(df["location"].get(i)["longitude"])

        ctg = df["category"][i]

        marking(lat, lon, ctg)

        # print(str(i) + ": " + str(lat) + ", " + str(lon))


def marking(lt, ln, ct):
    if ct not in crime_color.keys():
        ct = 'other-crime'

    # fg.add_child(
    #     folium.Marker(location=[lt, ln],
    #                   popup=ctg,
    #                   icon=folium.Icon(color=crime_color[ctg])))

    fg.add_child(folium.CircleMarker(location=[lt, ln], radius=8,
                                     popup=ct, fill_color=crime_color[ct], color="dark", fill_opacity=0.7))




if __name__ == '__main__':

    last_update = json.loads(urlopen("https://data.police.uk/api/crime-last-updated").read())
    print("Last updated: ", last_update['date'])

    while True:

        input_method = input("Address for 1, latitude and longitude for 2, close the app for 3: ")

        if (input_method == "1"):
            try:
                user_address = input("Please enter the address(as detail as possible): ")
                geolocator = ArcGIS(user_agent="ByeByeCrime")
                location = geolocator.geocode(user_address)
                print("Returned location is: " + location.address)
                print(location.latitude, location.longitude)
                user_lat = str(location.latitude)
                user_lon = str(location.longitude)
                try:
                    request(user_lat, user_lon)
                except:
                    print("Invalid address, try again, or input the latitude and longitude instead")
                    continue

            except:
                print("Invalid address, try again, or input the latitude and longitude instead")
                continue
            else:
                break
        elif (input_method == "2"):
            try:
                user_lat = input("Please enter the latitude: ")
                user_lon = input("Please enter the longitude: ")
                try:
                    request(user_lat, user_lon)
                except:
                    print("Invalid latitude or longitude, please try again")
                    continue

                # if(user_lat.isdigit() != True or user_lon.isdigit() != True):
                #     print("Invalid latitude or longitude, please try again lll")
                #     continue
            except:
                print("Invalid latitude or longitude, please try again")
                continue
            else:
                break

        elif (input_method == "3"):
            print("Closed")
            sys.exit()

        else:
            print("Invalid input, please try again")
            continue

    map = folium.Map(location=[user_lat, user_lon],
                     zoom_start=15,
                     titles="ByeByeCrime")
    map.add_child(fg)
    map.add_child((folium.Marker(location=(user_lat, user_lon), popup="You are here",
                                 icon=folium.Icon(color='blue', icon='user'))))
    map.save("ByeByeCrime.html")

    print("The map was generated successfully")
