"""
Goals:

Isabelle: Streamlit website, make AI object like Martini said to do
Emily: Get exoplanet files, add them to streamlit to be access, make into pandas dataframe
Gabby: Labels on skymap, add other skymap for below the horizon. Add stars that correspond to current sky position 

Next time: Combine exoplanet data to plot on skymap, show statistics of exoplanet (from pandas dataframe), get AI to give additional info about the exoplanet
"""



from litellm.llms.azure.completion.handler import prompt_factory
import streamlit as st
import warnings
import litellm
import os
import time

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from dotenv import load_dotenv
load_dotenv()

apiBase = "https://litellmproxy.osu-ai.org" 

astro1221Key = os.getenv("ASTRO1221_API_KEY")
if astro1221Key:
    print("Successfully loaded Astronomy 1221 key")
else:
    print("Error: did not find key. Check that .env exists in the same folder/directory as your class notebooks")

if os.path.isfile('.gitignore'):
    print("Successfully found .gitignore in the current directory")
else:
    print("Error: Did not find .gitignore. Please download .gitignore from carmen and put in the same folder/directory as your class notebooks.")

with open('.gitignore', 'r') as f:
    content = f.read()
    if '.env' in content:
        print("Confirmed that .gitignore has the .env exclusion")
    else: 
        print("Error: Did not find .env in .gitignore. Please download .gitignore from carmen and put with your class notebooks.")

def prompt_llm(messages, model="openai/GPT-4.1-mini", temperature=0.2, max_tokens=1000):
    """
    Send a prompt or conversation to an LLM using LiteLLM and return the response.

    Parameters:
        messages: Either a string (single user prompt) or a list of message dicts with
                  "role" and "content". If a string, formatted as [{"role": "user", "content": messages}].
        model (str, optional): The name of the model to use. Defaults to "openai/GPT-4.1-mini".
        temperature (float, optional): Value between 0 and 2; higher values make output more random. Defaults to 0.2.
        max_tokens (int, optional): Maximum number of tokens to generate in the completion. Must be a positive integer. Defaults to 1000.

    Prints the answer returned by the model.
    
    Returns:
        response: The full response object from LiteLLM.

    Raises:
        ValueError: If `temperature` is not in [0, 2] or `max_tokens` is not a positive integer.
    """
    # If messages is a string, format it as a single user message
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    # Validate temperature
    if not (isinstance(temperature, (int, float)) and 0 <= temperature <= 2):
        raise ValueError("temperature must be a float between 0 and 2 (inclusive).")
    # Validate max_tokens
    if not (isinstance(max_tokens, int) and max_tokens > 0):
        raise ValueError("max_tokens must be a positive integer.")

    answer = None

    try: 
        print("Contacting LLM via University Server...")

        response = litellm.completion(
            model=model,
            messages=messages,
            api_base=apiBase,
            api_key=astro1221Key,
            temperature=temperature,
            max_tokens=max_tokens
        )

        answer = response['choices'][0]['message']['content']
        print(f"\nSUCCESS! Here is the answer from {model}:\n")
        print(answer)
        print("\n")

    except Exception as e:
        print(f"\nERROR: Could not connect. Details:\n{e}")    
        response = None
        if answer is None:
            answer = "Sorry, there was an error connecting to the language model. Please try again."

    return answer

# streamlit run streamlit_exoplanet.py
st.title("Exoplanet")

option = st.selectbox(
    "Select an exoplanet:",
    ("HD 189733B", "Kepler 17B", "Kepler 20F"),
)

st.write("You selected:", option)

# Initialize
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
    response = prompt_llm(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)

#making a map of the sky and stuff
#skyfield for pretty star data
 
import numpy as np
import matplotlib.pyplot as plt

st.subheader("cute little sky circle")

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

    ax.set_aspect('equal')
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.axis('off')  # hide axes frame/ticks
 #maybe adding NSEW coordinates
    ax.text (0.5, 1.05, 'North', transform=ax.transAxes, ha='center', va='bottom', fontsize=12)
    st.pyplot(fig)

   