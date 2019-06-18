from flask import Flask, render_template, request
import pandas
from geopy.geocoders import ArcGIS
import folium
import matplotlib.pyplot as plt


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

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods = ['POST', 'GET'])
def byebyeresult():
    if request.method == 'POST':
        address = request.form
        geolocator = ArcGIS(user_agent="app_test")
        
        try:

            location = geolocator.geocode(address)
            lat = str(location.latitude)
            lon = str(location.longitude)
            start_coords = (lat, lon)

            folium_map = folium.Map(location=start_coords, zoom_start=16, width='75%', height='75%')
            df_request = "https://data.police.uk/api/crimes-street/all-crime?lat=" + str(lat) + "&" + "lng=" + str(lon)
            df = pandas.read_json(df_request)
            fg = folium.FeatureGroup(name="ByeByeCrime")

            total_crime = df["id"].size

            for i in range(total_crime):
                crime_lat = float(df["location"].get(i)["latitude"])
                crime_lon = float(df["location"].get(i)["longitude"])

                ctg = df["category"][i]

                if ctg not in crime_color.keys():
                    ctg = 'other-crime'



                fg.add_child(folium.CircleMarker(location=[crime_lat, crime_lon], radius=8,
                                                 popup=ctg, fill_color=crime_color[ctg], color="dark", fill_opacity=0.7))

            # plot()
            folium_map.add_child(fg)
            folium_map.add_child((folium.Marker(location=(lat, lon), popup="You are here",
                                                icon=folium.Icon(color='blue', icon='user'))))

            folium_map.save("templates/ByeByeCrime.html")



            return render_template("result.html", location_address = location.address, location_latitude = lat, location_longtitude = lon, total_crime = total_crime)
        except:
            return render_template("error.html")
#
# def plot():
#     left = [1, 2, 3, 4, 5]
#     height = [10, 24, 36, 40, 5]
#     tick_lable = ['one', 'two', 'three', 'four', 'five']
#     plt.bar(left, height, tick_lable=tick_lable, width=0.8, color = ['red', 'green'])
#     plt.xlabel('y - axis')
#     plt.xlabel('x - axis')
#     plt.title('My var chart!')
#     plt.savefig('static/images/plot.png')


if __name__ == '__main__':
    app.run(debug = True)