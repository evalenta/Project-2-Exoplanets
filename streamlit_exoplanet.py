# streamlit run streamlit_exoplanet.py

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

# Tells pandas to read the CSV file, but skips the first 97 rows since they are not part of the data that is needed and acts as headers
# the delimiter is a comma because the data is seperated by commas and each new planet is a new row
# loads in the exoplanet csv file the user downloaded
exoplanet = pd.read_csv('exoplanet.csv', skiprows=96, delimiter=',')

#changed df to df_exo to avoid confusion with df later in the code
# set row index as the planet's name for ease later
df_exo = exoplanet.set_index("pl_name")
# filtered exoplanets to filter out multiple observations of the same exoplanet
filtered_exo = dict.fromkeys(df_exo.index)

# exoplanet concept images for streamlit user reference
neptunelike_planet = 'neptunelike_planet.jpeg'
superearth_planet = 'superearth_planet.jpeg'
terrestrial_planet = 'terrestrial_planet.jpeg'
unkown_planet = 'unkown_planet.jpeg'
gasgiant = 'gasgiant.jpeg'

planet_type = [neptunelike_planet, superearth_planet, terrestrial_planet, unkown_planet, gasgiant]

# set title for streamlit app
st.title("Exoplanet Explorer")
st.set_page_config(layout="wide") 

# create chatbot object, use API key, etc.
chatbot = llmCall()

# divide streamlit app into columns
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Exoplanet Selection")
    st.write("Select an exoplanet from the list below to start your journey!")
    option = st.selectbox(
    label= "Select an exoplanet:",
    options = filtered_exo
    )
    st.write("You selected:", option)

    # the observations of that specific exoplanet
    planet_data_row = df_exo.loc[option]
    data = planet_data_row

    # chatbot classifies the exoplanet type
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

    # display exoplanet type's corresponding image
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

    # show observation data from NASA exoplanet csv to the user
    st.write(f"Here is observation data of {option}:")
    st.write(planet_data_row)

with col2:
    # put chat_input_bar at the bottom of the page
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
    st.write("Ask AI a question about the selected exoplanet:")

    change_chatbot_style()

    # set up message history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    else:
    # Validate that messages are dictionaries, reset if corrupted
        if st.session_state.messages and not isinstance(st.session_state.messages[0], dict):
            st.session_state.messages = []

    # Display message history on streamlit
    for msg in st.session_state.messages:
    # Ensure msg is a dictionary with required keys
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # User asks questions about the exoplanet
    if prompt := st.chat_input("Type here"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        # write the user's prompt in the chatbot interface
        with st.chat_message("user"):
            st.write(prompt)
        # Getting info on selected exoplanet from csv file so the AI can read it
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
        # add the AI's response to the chatbot interface
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

    # Load in Vizier catalog 
    vizier = Vizier(columns=["*", 'RA2000', 'DE2000'], row_limit=-1)
    # Vizier catalog of brightest stars in the night sky
    catalogs = vizier.get_catalogs("V/53A/catalog")
    # convert catalog to pandas dataframe
    df = catalogs[0].to_pandas()

    # rename columns for easier use
    df = df.rename(columns={
        "RA2000": "ra_degrees",
        "DE2000": "dec_degrees"
    })

    # User location (assumed to be columbus)
    columbus_lat = 39.9612   # degrees North
    columbus_lon = -83.0003  # degrees East 
    columbus_elev = 260      # meters above sea level 

    columbus_topos = wgs84.latlon(columbus_lat, columbus_lon, elevation_m=columbus_elev)

    # set observer location 
    observer = earth + columbus_topos

    # split sexagesimal ra and dec to convert to degrees then to radians
    ra_split, dec_split = df["ra_degrees"].str.split(expand=True).astype(float), df["dec_degrees"].str.split(expand=True)

    h = ra_split[0].values
    m = ra_split[1].values
    s = ra_split[2].values

    # convert from sexagesimal to radians and create new df column for ra radians
    df['RA_rad'] = (h + m/60 + s/3600) * (np.pi / 12)

    ra = df['RA_rad']

    # Since declination can be negative, we don't want it to mess with the calculation
    sign = np.where(dec_split[0].str.contains('-'), -1, 1)
    d = dec_split[0].str.replace('+', '', regex=False).str.replace('-', '', regex=False).astype(float).values
    min = dec_split[1].astype(float).values
    sec = dec_split[2].astype(float).values

    # convert to degrees and create new df column for dec degrees
    df['Dec_deg'] = sign * (d + (min/60) + (sec/3600))

    dec = df['Dec_deg']

    # create star object for alt/az skymap
    stars = Star(ra_hours=(h, m, s), dec_degrees=dec)

    # observe the stars from the observer's position (Columbus)
    astrometric = observer.at(t).observe(stars)
    apparent = astrometric.apparent()
    alt, az, distance = apparent.altaz()

    # add the alt and az to the df
    df["alt_deg"] = alt.degrees
    df["az_deg"] = az.degrees
    
    theta = ra
    # we want the zenith at the center
    r = 90.0 - dec

    # get magnitudes of stars to adjust star sizes on map
    vmag = df['Vmag'].fillna(df['Vmag'].mean())
    base_size = (8 - vmag).clip(lower=0.5) 
    star_sizes = 5 * np.exp(-0.7 * df['Vmag'].fillna(6))
    
    # get the ra and dec of the selected exoplanet
    exo_ra = planet_data_row["ra"]
    exo_dec = planet_data_row["dec"]
    
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="polar", facecolor="darkblue")

    # reset polar plot so 0 is at the top (where pi/2 normally is) and the plot goes clockwise instead of counter-clockwise
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    # plot the stars
    ax.scatter(theta, r, c="white", alpha=0.9, s=star_sizes)
    # plot the selected exoplanet
    ax.scatter(exo_ra, exo_dec, color='red', s=50, zorder=5,
        marker='o', edgecolors='darkred', linewidth=2)
    
    ax.set_xlim(0, 2 * np.pi)
    ax.set_yticks([0, 30, 60, 90, 120, 150, 180])
    ax.set_yticklabels(['+90°', '+60°', '+30°', '0°', '-30°', '-60°', '-90°'], c="white")
    ax.tick_params(colors="white") 
    st.pyplot(fig)
    
    # get alt and az in degrees
    alt_deg = alt.degrees
    az_deg = az.degrees

    # convert az to radians for polar plot
    theta2 = np.deg2rad(az_deg)
    # put zenith at the center
    r2 = 90.0 - alt_deg
    
    # get magnitudes of stars to adjust star sizes on the map
    vmag2 = df['Vmag'].fillna(df['Vmag'].mean())
    base_size2 = (8 - vmag2).clip(lower=0.5) 
    star_sizes2 = 5 * np.exp(-0.7 * df['Vmag'].fillna(6))

    fig2 = plt.figure(figsize=(6,6))
    ax2 = fig2.add_subplot(111, projection="polar", facecolor="darkblue")
    
    # reset polar plot so 0 is at the top (where pi/2 normally is) and the plot goes clockwise instead of counter-clockwise
    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)

    # plot stars
    ax2.scatter(theta2, r2, s=star_sizes2, c="white")

    ax2.set_xlim(0, 2 * np.pi)
    ax2.set_yticks([0, 30, 60, 90, 120, 150, 180])
    ax2.set_yticklabels(['+90°', '+60°', '+30°', '0°', '-30°', '-60°', '-90°'], color="white")
    ax2.tick_params(colors="white")

    ax2.set_title("Stars above horizon (Alt/Az)", color="white", pad=12)
    st.subheader("Alt and Az (Observing from Columbus, Ohio)")

    st.pyplot(fig2)