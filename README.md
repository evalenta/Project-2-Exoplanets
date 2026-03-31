# Project-2-Exoplanets

Before proceeding with the code please download the data on the following link as a CSV file: https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PS. Name this file as exoplanet.csv.

This is the Vizier catalog used for the stars on the starmap: https://vizier.u-strasbg.fr/viz-bin/VizieR-4

The goal of our code is to create a fully functioning streamlit that takes a closer look at exoplanets in an interactive way. Before continuing with the code, it is extremely important to double check that the exoplanet catalog is downloaded as a CSV into the users computer. Without this Csv file, the code will not run correctly or smoothly. Upon opening up the streamlit, a user is met with a website that is separated into 3 different columns. The first column is labeled Exoplanet Selection. This is the start of the magic; the user will pick from somewhere around 6,000 exoplanets. After making a selection, there will be an image that portrays the type of exoplanet--terrestrial, gas giant, Neptune-like, super earth, or unknown. Underneath this image there will be an additional column of information that looks at all the observations included in the CSV file for that specific exoplanet. The second column offers additional information on the chosen exoplanet. This is where the LLM comes in to answer questions, and after answering this question, there is a JSON block that give the exoplanet name, type, and the distance if this information is given in the csv file. The chat with the AI does not clear itself, so when you switch to a different exoplanet, previous conversations can still be viewed should the user want to look back on information. The final and third column shows a visual representation of where the exoplanet lies based on RA and DEC. There are additional stars that are on this visual, with larger stars being the brightest, and the smaller ones being dimmer. The large red dot shows where the exoplanet is. 



