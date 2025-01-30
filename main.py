from flask import Flask, request, render_template_string
from geopy.distance import geodesic
import folium
import pandas as pd

app = Flask(__name__)

# Load the data
df = pd.read_csv('./data/opendata_project.csv')
df = df[['project_id', 'name_th', 'price_min', 'developer_name_th', 'latitude', 'longitude', 'url_project', 'propertytype_name_th', 'date_created']]
df['price_min'] = pd.to_numeric(df['price_min'], errors='coerce')
df['date_created'] = pd.to_datetime(df['date_created'], format='%Y-%m-%d', errors='coerce')
df = df[(df['price_min'] < 7000000) & (df['price_min'] > 3000000)]
df = df[(df['propertytype_name_th'] == 'บ้าน') | (df['propertytype_name_th'] == 'บ้านแฝด')]
df.dropna(subset=['developer_name_th'], inplace=True)

@app.route('/')
def index():
    return render_template_string(open('templates/index.html').read())

@app.route('/generate_map', methods=['POST'])
def generate_map():
    user_lat = float(request.form['latitude'])
    user_lon = float(request.form['longitude'])
    center_point = (user_lat, user_lon)
    radius_km = 20

    def is_within_radius(center, point, radius):
        if pd.isnull(point[0]) or pd.isnull(point[1]):
            return False
        return geodesic(center, point).km <= radius

    df['is_within_radius'] = df.apply(lambda row: is_within_radius(center_point, (row['latitude'], row['longitude']), radius_km), axis=1)
    filtered_df = df[df['is_within_radius']]

    # Create the map
    map_center = folium.Map(location=center_point, zoom_start=13)

    # Add a marker for the center point
    folium.Marker(center_point, popup='Your Location', icon=folium.Icon(color='red')).add_to(map_center)

    # Add markers for the filtered points
    for _, row in filtered_df.iterrows():
        popup_content = f"Name: {row['name_th']}<br>Developer: {row['developer_name_th']}<br>Price: {row['price_min']}<br>Link: <a href='{row['url_project']}' target='_blank'>{row['url_project']}</a>"
        folium.Marker(location=(row['latitude'], row['longitude']), popup=popup_content).add_to(map_center)

    # Add Click Event to Show Popup Information
    map_center.add_child(folium.ClickForMarker(popup=None))

    # Save the map to an HTML file
    map_center.save('templates/map.html')

    return render_template_string(open('templates/map.html').read())

if __name__ == '__main__':
    app.run(debug=True)