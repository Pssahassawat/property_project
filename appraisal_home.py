from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
import folium
import pandas as pd

# Load and Filter Your Dataset
df = pd.read_csv('./data/opendata_project.csv')
df = df[['project_id', 'name_th', 'price_min', 'developer_name_th', 'latitude', 'longitude', 'url_project', 'propertytype_name_th','date_created']]
df['price_min'] = pd.to_numeric(df['price_min'], errors='coerce')
df['date_created'] = pd.to_datetime(df['date_created'], format='%Y-%m-%d', errors='coerce')
df = df[(df['price_min'] < 7000000) & (df['price_min'] > 3000000)]
df = df[(df['propertytype_name_th'] == 'บ้าน') | (df['propertytype_name_th'] == 'บ้านแฝด')]
df.dropna(subset=['developer_name_th'], inplace=True)

# Define the Center Point and Radius
center_point = (13.755052813872567, 100.47036465177612)
radius_km = 20

# Define the Function to Check if a Point is Within the Radius
def is_within_radius(center, point, radius):
    if pd.isnull(point[0]) or pd.isnull(point[1]):
        return False
    return geodesic(center, point).km <= radius

# Apply the Function to Filter Records
df['is_within_radius'] = df.apply(lambda row: is_within_radius(center_point, (row['latitude'], row['longitude']), radius_km), axis=1)
filtered_df = df[df['is_within_radius']]

# Check if filtered_df contains data
print(filtered_df.head())

# Create the Map
map_center = folium.Map(location=center_point, zoom_start=13)

# Add the Center Point to the Map
folium.Marker(center_point, popup='Center Point', icon=folium.Icon(color='red')).add_to(map_center)

# Add the Filtered Points to the Map
for _, row in filtered_df.iterrows():
    popup_content = f"Field 1: {row['name_th']}<br>Field 2: {row['developer_name_th']}<br>Field 3: {row['price_min']}<br>Field 4: {row['url_project']}"
    folium.CircleMarker(location=(row['latitude'], row['longitude']), radius=2, color='blue', fill=True, fill_opacity=0.6, popup=popup_content).add_to(map_center)

# Save the Map
map_center.save('map.html')
print("Map saved as 'map.html'.")