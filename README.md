# **vlr.gg flask API** 🚀
This repository contains a Flask-based API for scraping and updating live data from VLR.gg, a popular website for VALORANT esports statistics.
The backend connects to a Firebase Realtime Database , where the data collected is stored in efficient and seamless manner to the database.

## What the repo contains : 

- **Live Match Schedule:** Endpoint to retrieve the upcoming match schedule from VLR.gg. The data is refreshed and stored in Firebase for real-time updates.
- **Live Match Results:** Endpoint to retrieve the most recent match results from VLR.gg,
- **Combined Match Stats:** Endpoint to obtain combined statistics for a specific match using the match link parameter.
- **Individual Match Stats:** Endpoint to retrieve individual player statistics for a specific match using the match link parameter. Each player's data is stored separately in Firebase.
- **Event Roster Scraper:** Endpoint to scrape player rosters for a specific esports event using the event URL parameter. The data is stored in Firebase with a unique node based on the event name

## Tech-stack used

- **Python Flask:** Web framework for building the API.  
- **BeautifulSoup:** Python library for web scraping.   
- **Firebase Realtime Database:** Cloud-based NoSQL database for storing live data.   
- **Requests:** HTTP library for making web requests.   
- **Firebase Admin SDK:** To interact with Firebase from the backend.   

## Screenshots :

**Flask api json vs vlr.gg official website UI :**
![image](https://github.com/HarshitYaadav/vlr.ggAPI/assets/121128576/02ef1eaf-6d86-4f12-b2f4-8d6ae1a56fe1) ![image](https://github.com/HarshitYaadav/vlr.ggAPI/assets/121128576/c34eee18-42d9-4f04-83ed-0d850865a9a0)  

Firebase Realtime DB : ![image](https://github.com/HarshitYaadav/vlr.ggAPI/assets/121128576/60f8ead5-5802-4f41-899a-c4805625ba68)




