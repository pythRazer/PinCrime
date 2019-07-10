from flask import Flask, render_template, request
import pandas
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt, mpld3
from urllib.request import urlopen
import json

# The crime type list
crime_type = ['anti-social-behaviour', 'bicycle-theft', 'burglary', 'criminal-damage-arson', 'drugs', 'other-theft',
              'possession-of-weapons', 'public-order', 'robbery', 'shoplifting', 'theft-from-the-person',
              'vehicle-crime', 'violent-crime', 'other-crime']

# The dot's color
color = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
         'cadetblue', 'gray', 'pink', 'lightgreen']

# The initial count for each crime type
count = [0] * 14

# Dictionary {crime type : color}
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

# Dictionary {crime type : count}
crime_count = {zip(crime_type, count)}

# Starting Flask
app = Flask(__name__)

# Home page
@app.route('/')
def home():
    # Read the date of last update from api
    # Json file
    newJson = json.loads(urlopen("https://data.police.uk/api/crime-last-updated").read())
    # Get the date
    last_updated = newJson['date']
    # Return home.html, the last date of the update
    return render_template('home.html', last_updated=last_updated)

# Pie Chart page
@app.route('/Pie_Chart', methods=['GET'])
def statistics():
    # Return the html contains the pie chart image of the total crime in England which was made before by ourselves
    return render_template('Pie_Chart.html')

# Result page
@app.route('/result', methods=['POST', 'GET'])
def pin_crime_result():

    # Get the input
    if request.method == 'POST':
        address = request.form
        address = address['Address']

        # Start to try to paste the user's input to geolocator to get the location's detail
        try:
            geolocator = Nominatim(user_agent="app_test", timeout=10)
            location = geolocator.geocode(address, addressdetails=True)

            # The dictionary about the address from geocode's raw data
            address_dict = location.raw['address']

            # county = address_dict['county']


            # Try to get the county, if it is not in the dictionary, get the city instead
            try:
                county = address_dict['county']
            except:
                county = address_dict['city']


            # Get the latitude and the longitude of the place
            lat = str(location.latitude)
            lon = str(location.longitude)
            # The start coordinate
            start_coords = (lat, lon)

            # Initialize the folium map
            folium_map = folium.Map(location=start_coords, zoom_start=14, width='90%', height='80%')
            # Request the crime data
            # Pasting latitude and longitude to the url of data frame request
            df_request = "https://data.police.uk/api/crimes-street/all-crime?lat=" + str(lat) + "&" + "lng=" + str(lon)

            # Using pandas to read the json file sent back from the api
            df = pandas.read_json(df_request)

            # Having a feature group of all Crime Pins
            cpFG = folium.FeatureGroup(name="Crime Pins")

            # The total number of the crime
            total_crime = df["id"].size

            # Empty list of the crime's latitude and longitude
            crime_latlon = []

            # Pin the crimes
            for i in range(total_crime):
                # Get crimes latitude and longitude from the data frame
                crime_lat = float(df["location"].get(i)["latitude"])
                crime_lon = float(df["location"].get(i)["longitude"])
                # Append the empty list of crime's latitude and longitude
                crime_latlon.append([crime_lat, crime_lon])

                # Get the category of the crimes
                ctg = df["category"][i]

                # If the category does not match the crime_color dictionary, set the category to 'other-crime'
                if ctg not in crime_color.keys():
                    ctg = 'other-crime'

                # Add the crime to the feature group
                # Using circle marker to pin the crime, and fill the circle by the color related to that crime
                cpFG.add_child(folium.CircleMarker(location=[crime_lat, crime_lon], radius=8,
                                                 tooltip=ctg, fill_color=crime_color[ctg], color="dark",
                                                 fill_opacity=0.7))

                # Count the number for each crime
                for j in range(len(crime_type)):
                    if ctg == crime_type[j]:
                        count[j] += 1

            # Another feature group for the user(his/her input location)
            usFG = folium.FeatureGroup(name="User")
            # Using marker for pinning the user's location
            usFG.add_child((folium.Marker(location=(lat, lon), tooltip="You are here",
                                         icon=folium.Icon(color='blue', icon='user'))))

            # Create the heat map for crimes
            heat_map = HeatMap(data=crime_latlon, name='Contour map')
            # Add all feature groups to the map
            folium_map.add_child(cpFG)
            folium_map.add_child(usFG)
            folium_map.add_child(heat_map)
            # Have the layer control for filtering
            folium_map.add_child(folium.LayerControl())

            # Save the map to PinCrimes.html
            folium_map.save("templates/PinCrimes.html")

            # crime_types = ['\n'.join(wrap(l, 12)) for l in crime_type]

            # Generate the bar for the statistics of the crimes by matplotlib
            fig = plt.figure(figsize=(20, 6))
            x = range(14)
            plt.bar(x, count)
            plt.xticks(x, crime_type)

            # Using mpld3 to save the statistics result
            # Clear the plugins of mpld3
            mpld3.plugins.clear(fig)
            mpld3.save_html(fig, "templates/Pie_Chart.html", no_extras=True, template_type="simple")

            # Generate the url for facebook comment depending on the county(or city, if there is no data for county)
            fb_url = "http://0.0.0.0:5000/result?" + county
            # Replace the white space to +
            fb_url = fb_url.replace(" ", "+")
            # Checking the facebook comment's url
            print(fb_url)

            # Return the address, number of the crimes, county, and facebook comment's url to result.html
            return render_template("result.html", location_address=location.address,

                                   total_crime=total_crime, county=county, url=fb_url)
        # If it fails, return the error page
        except:
            return render_template("error.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=True, debug=True)
