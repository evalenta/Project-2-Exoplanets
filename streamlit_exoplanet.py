"""
Goals:

Isabelle: Streamlit website, make AI object like Martini said to do
Emily: Get exoplanet files, add them to streamlit to be access, make into pandas dataframe, add that to exoplanet dropdown options
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
from astroquery.vizier import Vizier
from astropy.coordinates import Angle
import pandas as pd
import csv

#MIGHT NEED TO DELETE
# Tells pandas to read the CSV file, but skips the first 97 rows since they are not part of the data that is needed and acts as headers
# the delimeter is a comma because the data is seperated by commas and each new planet is a new row
# uses .head() to print only the first 5 rows of data
exoplanet = pd.read_csv('exoplanet.csv', skiprows=97, delimiter=',')
#changed df to df_exo to avoid confusion with df later in the code
df_exo = pd.DataFrame(exoplanet)
exoplanet_list = df_exo.iloc[:,0].tolist()
exoplanet_name = list(dict.fromkeys(exoplanet_list))


# streamlit run streamlit_exoplanet.py
st.title("Exoplanet")
st.set_page_config(layout="wide") 

chatbot = llmCall()

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Column 1")
    st.write("Content for column 1")
    option = st.selectbox(
    label= "Select an exoplanet:",
    options = exoplanet_name
    )
    st.write("You selected:", option)

with col2:

    def change_chatbot_style():
    # Set style of chat input so that it shows up at the bottom of the column
        chat_input_style = f"""
        <style>
            .stChatInput {{
            position: fixed;
            bottom: 3rem;
            }}
        </style>
        """
        st.markdown(chat_input_style, unsafe_allow_html=True)

    st.header("Ai Chat Box")
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
        planet_data_row = df_exo[df_exo.iloc[:, 0] == option].to_string()
        full_prompt = f"""
        User is asking about the planet: {option}.
        Here is the data on the exoplanet from the CSV file:
        {planet_data_row}

        Question: {prompt}

        Please answer the question using the data above.
        Then, provide a JSON block with: {{ "name": "{option}", "type": "...", "distance": "..." }}
        """
        response = chatbot.ask_llm(full_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

with col3:
    st.header("Sky Map")
    st.write("Find the exoplanet on the sky map")
    st.subheader("cute little sky circle")

#setting up skyfield
    ts = load.timescale()
    t = ts.now()
    #with load.open("hip_main.dat") as f:
    #    df = hipparcos.load_dataframe(f)
    earth = load('de421.bsp')['earth']

    vizier = Vizier(columns=["*", 'RA2000', 'DE2000'], row_limit=-1)
    catalogs = vizier.get_catalogs("V/53A/catalog")
    df = catalogs[0].to_pandas()

    df = df.rename(columns={
        "RA2000": "ra_degrees",
        "DE2000": "dec_degrees"
    })

    #st.write(df["ra_degrees"])
    
    #stars = Star.from_dataframe(df)

    #observer = earth + Topos('40.0 N', '83.0 W') #coords for columbus, ohio
    #astrometric = observer.at(t).observe(stars)
    ra_split, dec_split = df["ra_degrees"].str.split(expand=True).astype(float), df["dec_degrees"].str.split(expand=True)

    h = ra_split[0].values
    m = ra_split[1].values
    s = ra_split[2].values

    df['RA_rad'] = (h + m/60 + s/3600) * (np.pi / 12)

    ra = df['RA_rad']

    sign = np.where(dec_split[0].str.contains('-'), -1, 1)
    d = dec_split[0].str.replace('+', '', regex=False).str.replace('-', '', regex=False).astype(float).values
    m = dec_split[1].astype(float).values
    s = dec_split[2].astype(float).values

    df['Dec_deg'] = sign * (d + (m/60) + (s/3600))

    dec = df['Dec_deg']

    if st.button("Show circle with grid"):
        
        theta = ra
        r = 90.0 - dec
        vmag = df['Vmag'].fillna(df['Vmag'].mean())

        base_size = (8 - vmag).clip(lower=0.5) 
        star_sizes = 5 * np.exp(-0.7 * df['Vmag'].fillna(6))



        
        fig = plt.figure(figsize=(6, 6))

        ax = fig.add_subplot(111, projection="polar", facecolor="darkblue")

        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)

        ax.scatter(theta, r, c="white", alpha=0.9, s=star_sizes)
        
        ax.set_xlim(0, 2 * np.pi)
        ax.set_yticks([0, 30, 60, 90])
        ax.set_yticklabels(['+90°', '+60°', '+30°', '0°'], c="white") 
        
        st.pyplot(fig)
        

        # Draw outer circle (radius 1)
        #circle = plt.Circle((0, 0), 1, edgecolor='white', facecolor='darkblue')
        #ax.add_artist(circle)

        # Radial gridlines (concentric circles)
        #for r in [0.25, 0.5, 0.75]:
            #ring = plt.Circle((0, 0), r, edgecolor='gray', facecolor='none', linewidth=0.5)
            #ax.add_artist(ring)

        # Angular gridlines (spokes)
        #for angle_deg in range(0, 360, 30):
            #angle = np.deg2rad(angle_deg)
            #x = np.cos(angle)
            #y = np.sin(angle)
            #ax.plot([0, x], [0, y], color='gray', linewidth=0.5)

        # Filter: Only stars above 0 degrees and brighter than magnitude 5.0
        #mask = (alt.degrees > 0) & (df['magnitude'] < 5.0)
        
        # (90 - alt)/90 scales Zenith to 0 and Horizon to 1.0
        #r_s = (90 - alt.degrees[mask]) / 90
        # Azimuth 0 is North. Rotated to match 'N' at the top
        #theta_s = np.deg2rad(az.degrees[mask] + 90) 
        
        #ax.scatter(-r_s * np.cos(theta_s), r_s * np.sin(theta_s), s=2, color='white', alpha=0.7)

        #ax.set_aspect('equal')
        #ax.set_xlim(-1.05, 1.05)
        #ax.set_ylim(-1.05, 1.05)
        #ax.axis('off')  # hide axes frame/ticks
    #maybe adding NSEW coordinates
        #ax.text(0.5, 1.05, 'N', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        #ax.text(0.5, -0.05, 'S', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        #ax.text(1.05, 0.5, 'E', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        #ax.text(-0.05, 0.5, 'W', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')

        #st.pyplot(fig)

    #st.subheader("cute little sky circle2")

    #if st.button("Show circle with grid2"):
        #fig, ax = plt.subplots(figsize=(6, 6))

        # Draw outer circle (radius 1)
        #circle = plt.Circle((0, 0), 1, edgecolor='white', facecolor='darkblue')
        #ax.add_artist(circle)

        # Radial gridlines (concentric circles)
        #for r in [0.25, 0.5, 0.75]:
            #ring = plt.Circle((0, 0), r, edgecolor='gray', facecolor='none', linewidth=0.5)
            #ax.add_artist(ring)

        # Angular gridlines (spokes)
        #for angle_deg in range(0, 360, 30):
            #angle = np.deg2rad(angle_deg)
            #x = np.cos(angle)
            #y = np.sin(angle)
            #ax.plot([0, x], [0, y], color='gray', linewidth=0.5)

            # Filter: Only stars below 0 degrees
        #mask_below = (alt.degrees <= 0) & (df['magnitude'] < 5.0)
        
        
        #r_b = (90 + alt.degrees[mask_below]) / 90
        #theta_b = np.deg2rad(az.degrees[mask_below] + 90)
        
        #ax.scatter(-r_b * np.cos(theta_b), r_b * np.sin(theta_b), s=2, color='white', alpha=0.5)

        #ax.set_aspect('equal')
        #ax.set_xlim(-1.05, 1.05)
        #ax.set_ylim(-1.05, 1.05)
        #ax.axis('off')  # hide axes frame/ticks
    #maybe adding NSEW coordinates
        #ax.text(0.5, 1.05, 'N', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        #ax.text(0.5, -0.05, 'S', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        #ax.text(1.05, 0.5, 'E', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        #ax.text(-0.05, 0.5, 'W', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
    
        #st.pyplot(fig)

