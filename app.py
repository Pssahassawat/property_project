import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static

# Load the data
df = pd.read_csv('./data/opendata_project.csv')
df = df[['project_id', 'name_th', 'price_min', 'developer_name_th', 'latitude', 'longitude', 'url_project', 'propertytype_name_th', 'date_created']]
df['price_min'] = pd.to_numeric(df['price_min'], errors='coerce')
df['date_created'] = pd.to_datetime(df['date_created'], format='%Y-%m-%d', errors='coerce')
df = df[(df['price_min'] < 7000000) & (df['price_min'] > 4000000)]
df = df[(df['propertytype_name_th'] == 'บ้าน') | (df['propertytype_name_th'] == 'บ้านแฝด')]
df.dropna(subset=['developer_name_th'], inplace=True)

# Define the default latitude and longitude
default_lat = 13.755044595496038
default_lon = 100.47044284884544

# Define the Streamlit app
def main():
    st.title('OpenData Project Map')

    # Get user input for latitude and longitude
    user_lat = st.number_input('Enter your latitude:', key='latitude', value=default_lat)
    user_lon = st.number_input('Enter your longitude:', key='longitude', value=default_lon)

    if st.button('Submit', key='submitButton'):
        if user_lat and user_lon:
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

            # Display the map
            folium_static(map_center)

if __name__ == '__main__':
    main()