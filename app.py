import streamlit as st
import requests
import random
from datetime import datetime, date, time
import pandas as pd
import pydeck as pdk
import glob
import random


'''
# 🚕 NYC TaxiFare Predictor
'''

NYC_BOUNDS = {
    "lon": (-74.03, -73.75),
    "lat": (40.63, 40.85)
}

def random_params():
    """Génère des paramètres aléatoires dans les bornes de NYC"""
    return {
        "date": date(random.randint(2009, 2015), random.randint(1, 12), random.randint(1, 28)),
        "time": time(random.randint(0, 23), random.randint(0, 59)),
        "pickup_lon": round(random.uniform(*NYC_BOUNDS["lon"]), 6),
        "pickup_lat": round(random.uniform(*NYC_BOUNDS["lat"]), 6),
        "dropoff_lon": round(random.uniform(*NYC_BOUNDS["lon"]), 6),
        "dropoff_lat": round(random.uniform(*NYC_BOUNDS["lat"]), 6),
        "passengers": random.randint(1, 4)
    }

# Bouton random AVANT les widgets pour initialiser le state
if st.button("🎲 Random parameters"):
    p = random_params()
    st.session_state.update(p)

# Valeurs par défaut si pas encore de state
defaults = {
    "date": date(2014, 7, 6),
    "time": time(19, 18),
    "pickup_lon": -73.950655,
    "pickup_lat": 40.783282,
    "dropoff_lon": -73.984365,
    "dropoff_lat": 40.769802,
    "passengers": 2
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# 1. Contrôleurs utilisateur
st.markdown("### Paramètres de la course")
col1, col2 = st.columns(2)

with col1:
    pickup_date = st.date_input("Date", value=st.session_state["date"], key="date")
    pickup_time = st.time_input("Heure", value=st.session_state["time"], key="time")
    pickup_longitude = st.number_input("Pickup Longitude", value=st.session_state["pickup_lon"], key="pickup_lon")
    pickup_latitude = st.number_input("Pickup Latitude", value=st.session_state["pickup_lat"], key="pickup_lat")

with col2:
    dropoff_longitude = st.number_input("Dropoff Longitude", value=st.session_state["dropoff_lon"], key="dropoff_lon")
    dropoff_latitude = st.number_input("Dropoff Latitude", value=st.session_state["dropoff_lat"], key="dropoff_lat")
    passenger_count = st.number_input("Passengers", min_value=1, max_value=8, value=st.session_state["passengers"], key="passengers")

#map
st.markdown("### 🗺️ Carte du trajet")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame({
        "lat": [pickup_latitude, dropoff_latitude],
        "lon": [pickup_longitude, dropoff_longitude],
        "color": [[0, 200, 0], [255, 0, 0]],  # vert = pickup, rouge = dropoff
        "label": ["Pickup", "Dropoff"]
    }),
    get_position="[lon, lat]",
    get_color="color",
    get_radius=150,
    get_label='label'
)

view = pdk.ViewState(
    latitude=(pickup_latitude + dropoff_latitude) / 2,
    longitude=(pickup_longitude + dropoff_longitude) / 2,
    zoom=12
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))

# 2. Paramètres API
params = {
    "pickup_datetime": f"{pickup_date} {pickup_time}",
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}


st.markdown("""
    <div style='text-align: left; font-size: 2em; animation: bounce 1s infinite;'>
        👇
    </div>
    <style>
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(10px); }
        }
    </style>
""", unsafe_allow_html=True)

url = 'https://taxifare-qn6uulpndq-ew.a.run.app/predict'
if st.button("Predict fare 🚀"):
    response = requests.get(url, params=params)

    if response.status_code == 200:
        fare = response.json()["fare"]
        st.success(f"💰 Estimated fare: **${fare:.2f}**")
        gifs = glob.glob("assets/*.gif")
        if gifs:
            st.image(random.choice(gifs))
    else:
        st.error("API error — check your URL or parameters")
        st.write(response.status_code)
        st.write(response.text)

st.markdown("---")
st.markdown("Made with ❤️ by **IoMaverick**")
