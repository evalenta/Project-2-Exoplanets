"""
Goals:

Isabelle: Streamlit website, make AI object like Martini said to do, connect AI to exoplanet choice, make skymap alt az instead of ra and dec
Emily: Get exoplanet files, add them to streamlit to be access, make into pandas dataframe, add that to exoplanet dropdown options, show "image" of exoplanet
Gabby: Labels on skymap, add other skymap for below the horizon. Add stars that correspond to current sky position 
new gabby goal; get llm to take info emily gets on exoplanets, have llm give additional info about the exoplanet mayhaps perhaps maybe
Next time: Combine exoplanet data to plot on skymap, show statistics of exoplanet (from pandas dataframe), get AI to give additional info about the exoplanet
"""



import streamlit as st
import warnings
import litellm
import os
import time
from llm_setup import llmCall
import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from skyfield.api import wgs84
from astroquery.vizier import Vizier
from astropy.coordinates import Angle
import pandas as pd
import csv
from astropy.coordinates import SkyCoord
from astropy import units as u


#MIGHT NEED TO DELETE
# Tells pandas to read the CSV file, but skips the first 97 rows since they are not part of the data that is needed and acts as headers
# the delimeter is a comma because the data is seperated by commas and each new planet is a new row
# uses .head() to print only the first 5 rows of data
exoplanet = pd.read_csv('exoplanet.csv', skiprows=96, delimiter=',')
#changed df to df_exo to avoid confusion with df later in the code

# images = pd.read_csv('planet_images.csv', delimiter=',')

df_exo = exoplanet.set_index("pl_name")
filtered_exo = dict.fromkeys(df_exo.index)

neptunelike_planet = 'neptunelike_planet.jpeg'
superearth_planet = 'superearth_planet.jpeg'
terrestrial_planet = 'terrestrial_planet.jpeg'
unkown_planet = 'unkown_planet.jpeg'
gasgiant = 'gasgiant.jpeg'

planet_type = [neptunelike_planet, superearth_planet, terrestrial_planet, unkown_planet, gasgiant]


#df_exo.index = df_exo.index.drop_duplicates(keep='first')




# streamlit run streamlit_exoplanet.py
st.title("Exoplanet Explorer")
st.set_page_config(layout="wide") 

chatbot = llmCall()

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Exoplanet Selection")
    st.write("Select an exoplanet from the list below to start your journey!")
    option = st.selectbox(
    label= "Select an exoplanet:",
    options = filtered_exo
    )
    st.write("You selected:", option)

    planet_data_row = df_exo.loc[option]
    data = planet_data_row

    assignment = f"""
    You will be given a specific exoplanet with information from a csv file. Using information from 
    research papers or websites online you can find, respond ONLY with the one of the following options 
    that best labels the exoplanet being asked by the user. The following options you have are below 
    and separated by commas:

    neptunelike_planet, superearth_planet, terrestrial_planet, unkown_planet, gasgiant

    Do not respond with any other information except for ONE of these labels.

    User is asking about the planet: {option}.
    Here is the data on the exoplanet from the CSV file: {data}"""

    exoplanet_type = chatbot.ask_llm(assignment)
    st.write(f"This planet is a {exoplanet_type}.\n The following is an example of what a {exoplanet_type} would look like.")
    if exoplanet_type == "neptunelike_planet":
        st.image('neptunelike_planet.jpg')
    elif exoplanet_type == "superearth_planet":
        st.image('superearth_planet.jpg')
    elif exoplanet_type == "terrestrial_planet":
        st.image('terrestrial_planet.jpg')
    elif exoplanet_type == "unknown_planet":
        st.image('unknown_planet.jpg')
    elif exoplanet_type == "gasgiant":
        st.image('gasgiant.jpeg')

    st.write(f"Here is observation data of {option}:")
    st.write(planet_data_row)

# test

with col2:

    def change_chatbot_style():
        """
        Set style of chat input so that it shows up at the bottom of the column. 
        """
        chat_input_style = f"""
        <style>
            .stChatInput {{
            position: fixed;
            bottom: 3rem;
            }}
        </style>
        """
        st.markdown(chat_input_style, unsafe_allow_html=True)

    st.header("Ai Chat Bot")
    st.write("Ask AI a question about the selected exoplanet")

    change_chatbot_style()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    else:
    # Validate that messages are dictionaries, reset if corrupted
        if st.session_state.messages and not isinstance(st.session_state.messages[0], dict):
            st.session_state.messages = []

        # Display history
    for msg in st.session_state.messages:
    # Ensure msg is a dictionary with required keys
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Handle input
    if prompt := st.chat_input("Type here"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        # Add response
        # Getting info on selected exoplanet from csv file and converting to string.
        data = planet_data_row
        full_prompt = f"""
        User is asking about the planet: {option}.
        Here is the data on the exoplanet from the CSV file:
        {data}

        Question: {prompt}

        Please answer the question using the data above and any information from research papers and websites found online.
        Then, provide a JSON block with: {{ "Name": "{option}", "Exoplanet type": "...", "Distance from Earth": "...", "Discovery year": "...", "Discovery Method": "...", "RA": "...", "Dec": "..." }}
        """
        response = chatbot.ask_llm(full_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

with col3:
    st.header("Sky Map")
    st.write("Find the exoplanet on the sky map")
    st.subheader("RA and Dec (with brightest stars in sky for reference)")

#setting up skyfield
    ts = load.timescale()
    t = ts.now()
    eph = load('de421.bsp')
    earth = eph['earth']

    vizier = Vizier(columns=["*", 'RA2000', 'DE2000'], row_limit=-1)
    catalogs = vizier.get_catalogs("V/53A/catalog")
    df = catalogs[0].to_pandas()

    df = df.rename(columns={
        "RA2000": "ra_degrees",
        "DE2000": "dec_degrees"
    })

    columbus_lat = 39.9612   # degrees North
    columbus_lon = -83.0003  # degrees East (negative = West)
    columbus_elev = 260      # meters above sea level

    columbus_topos = wgs84.latlon(columbus_lat, columbus_lon, elevation_m=columbus_elev)

    observer = earth + columbus_topos

    ra_split, dec_split = df["ra_degrees"].str.split(expand=True).astype(float), df["dec_degrees"].str.split(expand=True)

    h = ra_split[0].values
    m = ra_split[1].values
    s = ra_split[2].values

    df['RA_rad'] = (h + m/60 + s/3600) * (np.pi / 12)

    ra = df['RA_rad']

    sign = np.where(dec_split[0].str.contains('-'), -1, 1)
    d = dec_split[0].str.replace('+', '', regex=False).str.replace('-', '', regex=False).astype(float).values
    min = dec_split[1].astype(float).values
    sec = dec_split[2].astype(float).values

    df['Dec_deg'] = sign * (d + (min/60) + (sec/3600))

    dec = df['Dec_deg']

    stars = Star(ra_hours=(h, m, s), dec_degrees=dec)

    astrometric = observer.at(t).observe(stars)
    apparent = astrometric.apparent()
    alt, az, distance = apparent.altaz()

    df["alt_deg"] = alt.degrees
    df["az_deg"] = az.degrees
        
    theta = ra
    r = 90.0 - dec
    vmag = df['Vmag'].fillna(df['Vmag'].mean())

    base_size = (8 - vmag).clip(lower=0.5) 
    star_sizes = 5 * np.exp(-0.7 * df['Vmag'].fillna(6))
        
    exo_ra = planet_data_row["ra"]
    exo_dec = planet_data_row["dec"]
        
    fig = plt.figure(figsize=(6, 6))

    ax = fig.add_subplot(111, projection="polar", facecolor="darkblue")

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    ax.scatter(theta, r, c="white", alpha=0.9, s=star_sizes)
    ax.scatter(exo_ra, exo_dec, color='red', s=50, zorder=5,
        marker='o', edgecolors='darkred', linewidth=2)
        
    ax.set_xlim(0, 2 * np.pi)
    ax.set_yticks([0, 30, 60, 90])
    ax.set_yticklabels(['+90°', '+60°', '+30°', '0°'], c="white") 
        
    st.pyplot(fig)
    
    alt_deg = alt.degrees
    az_deg = az.degrees

    theta2 = np.deg2rad(az_deg)
    r2 = 90.0 - alt_deg
    
    vmag2 = df['Vmag'].fillna(df['Vmag'].mean())
    base_size2 = (8 - vmag2).clip(lower=0.5) 
    star_sizes2 = 5 * np.exp(-0.7 * df['Vmag'].fillna(6))

    fig2 = plt.figure(figsize=(6,6))
    ax2 = fig2.add_subplot(111, projection="polar", facecolor="midnightblue")
    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)

    ax2.scatter(theta2, r2, s=star_sizes2, c="white")

    ax2.set_xlim(0, 2 * np.pi)
    ax2.set_rticks([0, 30, 60, 90])
    ax2.set_yticklabels(["Zenith", "60°", "30°", "Horizon"], color="white")
    ax2.tick_params(colors="white")

    ax2.set_title("Stars above horizon (Alt/Az)", color="white", pad=12)

    st.subheader("Alt and Az (Observing from Columbus, Ohio)")

    st.pyplot(fig2)