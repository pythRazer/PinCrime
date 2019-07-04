from flask import Flask, render_template, request
import pandas
from geopy.geocoders import ArcGIS
import folium
from folium.plugins import HeatMap
from matplotlib import pyplot as plt
from textwrap import wrap

crime_type = ['anti-social-behaviour', 'bicycle-theft', 'burglary', 'criminal-damage-arson', 'drugs', 'other-theft',
              'possession-of-weapons', 'public-order', 'robbery', 'shoplifting', 'theft-from-the-person',
              'vehicle-crime', 'violent-crime', 'other-crime']

color = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
         'cadetblue', 'gray', 'pink', 'lightgreen']


count = [0] * 14
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

# crime_colors = {zip(crime_type, color)}

crime_count = {zip(crime_type, count)}

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')




@app.route('/result', methods=['POST', 'GET'])
def byebyeresult():
    if request.method == 'POST':
        address = request.form
        geolocator = ArcGIS(user_agent="app_test")

        # try:


        location = geolocator.geocode(address)
        # location_extent = location.raw['extent']
        # min_x = str(location_extent['xmin'])
        # min_y = str(location_extent['ymin'])
        # max_x = str(location_extent['xmax'])
        # max_y = str(location_extent['ymax'])
        # fb_return_url = "http://0.0.0.0:5000/result+minx" + min_x + "miny" + min_y + "max_x" + max_x + "max_y" + max_y

        lat = str(location.latitude)
        lon = str(location.longitude)
        start_coords = (lat, lon)



        folium_map = folium.Map(location=start_coords, zoom_start=14, width='80%', height='80%')
        df_request = "https://data.police.uk/api/crimes-street/all-crime?lat=" + str(lat) + "&" + "lng=" + str(lon)
        df = pandas.read_json(df_request)

        fg = folium.FeatureGroup(name="Crime Pins")

        total_crime = df["id"].size

        crime_latlon = []

        for i in range(total_crime):
            crime_lat = float(df["location"].get(i)["latitude"])
            crime_lon = float(df["location"].get(i)["longitude"])
            crime_latlon.append([crime_lat, crime_lon])

            ctg = df["category"][i]

            if ctg not in crime_color.keys():
                ctg = 'other-crime'

            fg.add_child(folium.CircleMarker(location=[crime_lat, crime_lon], radius=8,
                                             tooltip=ctg, fill_color=crime_color[ctg], color="dark",
                                             fill_opacity=0.7))

            for j in range(len(crime_type)):
                if ctg == crime_type[j]:
                    count[j] += 1


        fgu = folium.FeatureGroup(name="User")
        fgu.add_child((folium.Marker(location=(lat, lon), tooltip="You are here",
                                     icon=folium.Icon(color='blue', icon='user'))))


        heat_map = HeatMap(data=crime_latlon, name='Contour map')
        folium_map.add_child(fg)

        folium_map.add_child(fgu)
        folium_map.add_child(heat_map)
        folium_map.add_child(folium.LayerControl())

        folium_map.save("templates/PinCrimes.html")

        crime_types = ['\n'.join(wrap(l, 12)) for l in crime_type]
        plt.figure(figsize=(20, 10))
        plt.bar(crime_types, count)

        plt.savefig('static/new_plot.png')

        return render_template("result.html", location_address=location.address,

                               total_crime=total_crime)
    # except:
        #     return render_template("error.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=True, debug=True)