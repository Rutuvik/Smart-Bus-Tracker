Smart Bus Tracker — Real-Time Bus Monitoring System

This project demonstrates a real-time bus tracking and route visualization system built with FastAPI (backend) and Streamlit (frontend). It simulates live bus movements, displays dynamic routes, calculates delays, and provides ETA updates every few minutes — just like a real-world transport monitoring system.

 Overview

The Smart Bus Tracker solves a common urban problem: lack of visibility into real-time bus movement.
Using a simulated API, it tracks buses between two cities (e.g., Gondia → Nagpur), visualizes their routes, and updates bus positions automatically every 2 minutes.

Key objectives:

Real-time tracking & visualization

Route mapping with intermediate stops

Live ETA and delay status

Interactive bus selection interface

 Tech Stack
Component	Technology
Backend API	FastAPI
Frontend App	Streamlit
Visualization	PyDeck (Map Rendering)
Auto Refresh	Streamlit Autorefresh
Language	Python 3.12
Deployment Ready	 (can be hosted on GitHub + Render/Streamlit Cloud)
 How It Works

Backend (FastAPI)

/search_buses: Search for available buses between origin & destination.

/bus_location: Simulates live GPS movement and calculates ETA & delay.

/bus_stops: Returns stop names for the selected bus.

Frontend (Streamlit)

Users select origin, destination, and date.

Buses are listed with timing and type (AC/Non-AC).

On selecting a bus, the system fetches live data and draws:

Bus route line

Stop markers

 Arrival/Delay time dynamically updated

 Setup Instructions
1. Clone the Repository
git clone https://github.com/<your-username>/smart-bus-tracker.git
cd smart-bus-tracker

2. Create a Virtual Environment
python3 -m venv busapp_env
source busapp_env/bin/activate   
     
3. Install Dependencies
pip install -r requirements.txt

4. Run Backend (FastAPI)
uvicorn main:app --reload

5. Run Frontend (Streamlit)
streamlit run app_streamlit.py

 Features

✅ Real-time location tracking (auto-refresh every 2 minutes)
✅ Route line visualization with all stops
✅ ETA and delay updates
✅ Interactive map with hover tooltips
✅ Clean and modern interface

 Future Improvements

Integrate real GPS data from public transport APIs

Add passenger capacity tracking

Predict bus delays using machine learning

Build mobile-friendly dashboard

Include push notifications for arrival alerts

 Author

Rutvik Chavhan
Data Scientist & AI Engineer
📧 Email: chauhanrutvik42@gmail.com

🔗 GitHub: github.com/<Rutuvik>

🔗 LinkedIn: linkedin.com/in/rutvik-chavhan/

🏁 Final Note

This project isn’t just a simulation — it’s a scalable foundation for a real-time public transport tracking solution.
You can plug in GPS hardware or live APIs to make it fully production-ready.
