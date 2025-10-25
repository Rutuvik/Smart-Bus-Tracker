# app_streamlit.py -- robust single-file frontend
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import math
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
API_URL_SEARCH = "http://127.0.0.1:8000/search_buses"
API_URL_LOCATION = "http://127.0.0.1:8000/bus_location"
API_URL_STOPS = "http://127.0.0.1:8000/bus_stops"
UPDATE_INTERVAL = 120  # seconds
FALLBACK_CENTER = {"lat": 21.146, "lon": 79.089, "zoom": 11}

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Smart Bus Tracker", layout="wide")
st.title("🚌 Smart Bus Tracker — Stable & Debuggable")

# Auto-refresh
st_autorefresh(interval=UPDATE_INTERVAL * 1000, key="bus_refresh")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Search / Select Bus")
    origin = st.text_input("Origin", "Gondia")
    destination = st.text_input("Destination", "Nagpur")
    date = st.date_input("Travel Date")
    search_button = st.button("Search Buses")

# ---------------- SESSION STATE ----------------
if "bus_list" not in st.session_state:
    st.session_state.bus_list = []          # list of search results (dicts)
if "selected_bus_id" not in st.session_state:
    st.session_state.selected_bus_id = None

# ---------------- HELPERS: API CALLS ----------------
def safe_get(url, params=None, timeout=5):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def search_buses(origin, destination, date_str):
    data = safe_get(API_URL_SEARCH, params={"origin": origin, "destination": destination, "date": date_str})
    if data is None:
        return []
    return data.get("buses", [])

def get_bus_locations(bus_id=None):
    data = safe_get(API_URL_LOCATION, params={"bus_id": bus_id} if bus_id is not None else None)
    if data is None:
        return []
    return data.get("bus_locations", [])

def get_bus_stops(bus_id):
    data = safe_get(API_URL_STOPS, params={"bus_id": bus_id})
    if data is None:
        return []
    return data.get("stops", [])

# ---------------- SEARCH ACTION ----------------
if search_button:
    date_str = date.strftime("%Y-%m-%d")
    st.session_state.bus_list = search_buses(origin, destination, date_str)
    if not st.session_state.bus_list:
        st.warning("No buses found for this route/date. Try a different date or origin/destination.")
    else:
        # set default selection to first bus if none selected
        if st.session_state.selected_bus_id is None:
            st.session_state.selected_bus_id = st.session_state.bus_list[0]["bus_id"]

# local alias
bus_list = st.session_state.bus_list

# ---------------- SELECTION UI ----------------
if bus_list:
    st.sidebar.markdown("### Available buses")
    # show selectbox (keeps UI compact) and also buttons
    options = [f"{b['bus_id']} | {b['departure']} | {b['type']}" for b in bus_list]
    sel = st.sidebar.selectbox("Choose a bus", options, index=0)
    chosen_id = int(sel.split("|")[0].strip())
    # Button list (optional quick-select)
    for b in bus_list:
        if st.sidebar.button(f"Track {b['bus_id']} @ {b['departure']}", key=f"btn_{b['bus_id']}"):
            chosen_id = b["bus_id"]
    # update session state only if changed
    if chosen_id != st.session_state.selected_bus_id:
        st.session_state.selected_bus_id = chosen_id

# ---------------- UI placeholders ----------------
map_placeholder = st.empty()
st.sidebar.markdown("---")
info_col = st.sidebar.container()
debug_expander = st.expander("Debug: raw API responses")

# ---------------- MAP RENDER HELPERS ----------------
def fallback_map():
    vs = pdk.ViewState(latitude=FALLBACK_CENTER["lat"], longitude=FALLBACK_CENTER["lon"], zoom=FALLBACK_CENTER["zoom"])
    deck = pdk.Deck(layers=[], initial_view_state=vs)
    map_placeholder.pydeck_chart(deck)

def is_valid_coord(v):
    return isinstance(v, (int, float)) and not math.isnan(v)

def create_map(bus_locations, highlight_bus_id=None):
    # bus_locations: list of dicts from API (may contain multiple buses)
    if not bus_locations:
        fallback_map()
        st.warning("No bus location data returned from backend.")
        return

    # build DataFrame of valid markers
    rows = []
    for b in bus_locations:
        lat = b.get("lat")
        lon = b.get("lon")
        if is_valid_coord(lat) and is_valid_coord(lon):
            eta = b.get("eta")
            # treat non-numeric eta as large positive so color green
            try:
                eta_val = int(eta)
            except:
                eta_val = 9999
            color = [0,200,0] if eta_val >= 0 else [255,0,0]
            rows.append({
                "lat": lat, "lon": lon, "bus_id": b.get("bus_id"),
                "route": b.get("route",""), "eta": eta_val,
                "status": b.get("status",""), "next_stop": b.get("next_stop",""),
                "stops": b.get("stops", []), "color": color
            })
    if not rows:
        fallback_map()
        st.warning("API returned bus entries but none had valid lat/lon coordinates.")
        return

    df = pd.DataFrame(rows)

    # override colors to highlight selected bus
    if highlight_bus_id is not None:
        df["color"] = [
            [255,0,0] if int(bid)==int(highlight_bus_id) else col
            for bid,col in zip(df["bus_id"], df["color"])
        ]

    # Scatter layer for buses
    bus_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_color='color',
        get_radius=250,
        pickable=True
    )

    layers = [bus_layer]

    # If highlighted bus has stops with coords, draw path and stop markers
    highlighted = None
    if highlight_bus_id is not None:
        highlighted = next((b for b in bus_locations if int(b.get("bus_id"))==int(highlight_bus_id)), None)

    if highlighted and isinstance(highlighted.get("stops"), list) and highlighted["stops"]:
        stops_coords = [s for s in highlighted["stops"] if is_valid_coord(s.get("lat")) and is_valid_coord(s.get("lon"))]
        if stops_coords:
            route_coords = [[s["lon"], s["lat"]] for s in stops_coords]
            # Path layer (list under column 'path')
            route_df = pd.DataFrame({"path":[route_coords]})
            path_layer = pdk.Layer(
                "PathLayer",
                data=route_df,
                get_path="path",
                get_width=6,
                get_color=[0,0,255]
            )
            # stops scatter
            stop_df = pd.DataFrame(stops_coords)
            stop_layer = pdk.Layer(
                "ScatterplotLayer",
                data=stop_df,
                get_position='[lon, lat]',
                get_color=[255,165,0],
                get_radius=140,
                pickable=True
            )
            layers += [path_layer, stop_layer]

    # view center: center on highlighted bus if exists, else first marker
    center = df.loc[df["bus_id"]==highlight_bus_id].iloc[0] if highlight_bus_id in df["bus_id"].values else df.iloc[0]
    vs = pdk.ViewState(latitude=center["lat"], longitude=center["lon"], zoom=12, pitch=0)

    tooltip = {
        "html": "<b>Bus ID:</b> {bus_id} <br/>"
                "<b>Route:</b> {route} <br/>"
                "<b>Next Stop:</b> {next_stop} <br/>"
                "<b>ETA:</b> {eta} min <br/>"
                "<b>Status:</b> {status}",
        "style": {"backgroundColor":"white","color":"black","fontSize":14}
    }

    try:
        deck = pdk.Deck(layers=layers, initial_view_state=vs, tooltip=tooltip)
        map_placeholder.pydeck_chart(deck)
    except Exception as e:
        st.error(f"Map rendering error: {e}")
        fallback_map()

# ---------------- MAIN DISPLAY LOGIC ----------------
if st.session_state.selected_bus_id is not None:
    # fetch locations for the selected bus (API returns list)
    raw_locations = get_bus_locations(st.session_state.selected_bus_id)
    debug_expander.write({"bus_location_response": raw_locations})

    # Render map and layers
    create_map(raw_locations, highlight_bus_id=st.session_state.selected_bus_id)

    # Show stops and status (from the same API response)
    entry = next((x for x in raw_locations if int(x.get("bus_id", -1))==int(st.session_state.selected_bus_id)), None)
    if entry:
        stops = entry.get("stops", [])
        if stops and isinstance(stops, list):
            # mark next stop in bold
            next_stop = entry.get("next_stop", "")
            stops_str = " → ".join([f"**{s['name']}**" if s.get("name")==next_stop else s.get("name") for s in stops])
            st.markdown(f"**Route & Stops:** {stops_str}")
        else:
            st.info("Stops data not available (API did not provide lat/lon for stops).")

        # Show ETA and status prominently
        st.metric(label=f"Bus {entry['bus_id']} Status", value=str(entry.get("status","")), delta=f"Next: {entry.get('next_stop','')}")
    else:
        st.warning("Selected bus not present in API response. Map may be empty.")

else:
    # nothing selected: show fallback map and hint
    fallback_map()
    st.info("Search and select a bus from the sidebar to view live location, route, and ETA.")

# show debug panel at bottom for troubleshooting
with debug_expander:
    st.write("session_state:", {"selected_bus_id": st.session_state.selected_bus_id, "bus_list_len": len(bus_list)})
    st.write("bus_list:", bus_list)
