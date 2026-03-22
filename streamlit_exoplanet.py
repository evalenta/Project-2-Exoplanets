"""
Goals:

Isabelle: Streamlit website, make AI object like Martini said to do
Emily: Get exoplanet files, add them to streamlit to be access, make into pandas dataframe, add that to exoplanet dropdown options
Gabby: Labels on skymap, add other skymap for below the horizon. Add stars that correspond to current sky position 

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

# streamlit run streamlit_exoplanet.py
st.title("Exoplanet")
st.set_page_config(layout="wide") 

chatbot = llmCall()

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Column 1")
    st.write("Content for column 1")
    option = st.selectbox(
    "Select an exoplanet:",
    ("HD 189733B", "Kepler 17B", "Kepler 20F"),
    )
    st.write("You selected:", option)

with col2:
    st.header("Column 2")
    st.write("Content for column 2")
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
        response = chatbot.ask_llm(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

with col3:
    st.header("Column 3")
    st.write("Content for column 3")
    st.subheader("cute little sky circle")

#setting up skyfield
    ts = load.timescale()
    t = ts.now()
    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)
    earth = load('de421.bsp')['earth']
    observer = earth + Topos('40.0 N', '83.0 W') #coords for columbus, ohio

    if st.button("Show circle with grid"):
        fig, ax = plt.subplots(figsize=(6, 6))

        # Draw outer circle (radius 1)
        circle = plt.Circle((0, 0), 1, edgecolor='white', facecolor='darkblue')
        ax.add_artist(circle)

        # Radial gridlines (concentric circles)
        for r in [0.25, 0.5, 0.75]:
            ring = plt.Circle((0, 0), r, edgecolor='gray', facecolor='none', linewidth=0.5)
            ax.add_artist(ring)

        # Angular gridlines (spokes)
        for angle_deg in range(0, 360, 30):
            angle = np.deg2rad(angle_deg)
            x = np.cos(angle)
            y = np.sin(angle)
            ax.plot([0, x], [0, y], color='gray', linewidth=0.5)
            
            astrometric = observer.at(t).observe(Star.from_dataframe(df))
        alt, az, _ = astrometric.apparent().altaz()
        
        # Filter: Only stars above 0 degrees and brighter than magnitude 5.0
        mask = (alt.degrees > 0) & (df['magnitude'] < 5.0)
        
        # (90 - alt)/90 scales Zenith to 0 and Horizon to 1.0
        r_s = (90 - alt.degrees[mask]) / 90
        # Azimuth 0 is North. Rotated to match 'N' at the top
        theta_s = np.deg2rad(az.degrees[mask] + 90) 
        
        ax.scatter(-r_s * np.cos(theta_s), r_s * np.sin(theta_s), s=2, color='white', alpha=0.7)

        ax.set_aspect('equal')
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-1.05, 1.05)
        ax.axis('off')  # hide axes frame/ticks
    #maybe adding NSEW coordinates
        ax.text(0.5, 1.05, 'N', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        ax.text(0.5, -0.05, 'S', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        ax.text(1.05, 0.5, 'E', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        ax.text(-0.05, 0.5, 'W', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')

        st.pyplot(fig)

    st.subheader("cute little sky circle2")

    if st.button("Show circle with grid2"):
        fig, ax = plt.subplots(figsize=(6, 6))

        # Draw outer circle (radius 1)
        circle = plt.Circle((0, 0), 1, edgecolor='white', facecolor='darkblue')
        ax.add_artist(circle)

        # Radial gridlines (concentric circles)
        for r in [0.25, 0.5, 0.75]:
            ring = plt.Circle((0, 0), r, edgecolor='gray', facecolor='none', linewidth=0.5)
            ax.add_artist(ring)

        # Angular gridlines (spokes)
        for angle_deg in range(0, 360, 30):
            angle = np.deg2rad(angle_deg)
            x = np.cos(angle)
            y = np.sin(angle)
            ax.plot([0, x], [0, y], color='gray', linewidth=0.5)

            # Filter: Only stars below 0 degrees
        mask_below = (alt.degrees <= 0) & (df['magnitude'] < 5.0)
        
        
        r_b = (90 + alt.degrees[mask_below]) / 90
        theta_b = np.deg2rad(az.degrees[mask_below] + 90)
        
        ax.scatter(-r_b * np.cos(theta_b), r_b * np.sin(theta_b), s=2, color='white', alpha=0.5)

        ax.set_aspect('equal')
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-1.05, 1.05)
        ax.axis('off')  # hide axes frame/ticks
    #maybe adding NSEW coordinates
        ax.text(0.5, 1.05, 'N', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        ax.text(0.5, -0.05, 'S', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        ax.text(1.05, 0.5, 'E', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
        ax.text(-0.05, 0.5, 'W', transform=ax.transAxes, ha='center', va='bottom', fontsize=15, color='red')
    
        st.pyplot(fig)

