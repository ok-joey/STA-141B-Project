import folium
import pandas as pd
import plotly.express as px
from main import final_data
import os
from pathlib import Path

# change to your own API key
api_key = "XK08ecDgAvtknAoRfyaneoTEnF6MmLermYZSgQ/D3d8="

# -----MAP SET UP-----

lat = 38
lon = -96
zoomLvl = 3.5

# set up map
m = folium.Map(location = [lat, lon], 
               control_scale = True,
               zoom_control = True,
               zoom_start = zoomLvl,
               min_zoom = zoomLvl,
               max_bounds=True,
               max_lat = 90,
               min_lat = -10,
               min_lon = -200,
               max_lon = -50,
               )

# set up figure 
fig = folium.Figure(width = 700, height = 400)
fig.add_child(m)


# -----IMPORTING DATA (JOBS + COORDS)-----

# import job listing information
df = final_data(api_key)

# split locations into city and state columns
df[['City', 'State']] = df['Locations'].str.split(pat=',', n=1, expand=True)
df['City'] = df['City'].str.strip()
df['State'] = df['State'].str.strip()

# import coordinate csv
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH1 = BASE_DIR / "data" / "uscities.csv"
cities_df = pd.read_csv(DATA_PATH1)

# rename columns to align with main data frame
cities_df = cities_df.rename(columns={
    'city': 'City',
    'state_id': 'StateAbbrev',
    'lat': 'lat',
    'lng': 'lon'
})

# dictionary mapping for full state names to abbreviations
us_state_abbrev = {
    'Alabama': 'AL','Alaska': 'AK','Arizona': 'AZ','Arkansas': 'AR','California': 'CA',
    'Colorado': 'CO','Connecticut': 'CT','Delaware': 'DE','Florida': 'FL','Georgia': 'GA',
    'Hawaii': 'HI','Idaho': 'ID','Illinois': 'IL','Indiana': 'IN','Iowa': 'IA',
    'Kansas': 'KS','Kentucky': 'KY','Louisiana': 'LA','Maine': 'ME','Maryland': 'MD',
    'Massachusetts': 'MA','Michigan': 'MI','Minnesota': 'MN','Mississippi': 'MS','Missouri': 'MO',
    'Montana': 'MT','Nebraska': 'NE','Nevada': 'NV','New Hampshire': 'NH','New Jersey': 'NJ',
    'New Mexico': 'NM','New York': 'NY','North Carolina': 'NC','North Dakota': 'ND','Ohio': 'OH',
    'Oklahoma': 'OK','Oregon': 'OR','Pennsylvania': 'PA','Rhode Island': 'RI','South Carolina': 'SC',
    'South Dakota': 'SD','Tennessee': 'TN','Texas': 'TX','Utah': 'UT','Vermont': 'VT',
    'Virginia': 'VA','Washington': 'WA','West Virginia': 'WV','Wisconsin': 'WI','Wyoming': 'WY'
}

# convert state names to abbreviations
df['StateAbbrev'] = df['State'].map(us_state_abbrev)

# merge data frames
df = df.merge(
    cities_df[['City', 'StateAbbrev', 'lat', 'lon']],
    on=['City', 'StateAbbrev'],
    how='left'
)

# drop rows with missing coordinates (cannot use for mapping)
df = df.dropna(subset=['lat', 'lon'])

# change "Not Listed" -> "N/A" (too long of a value, looks bad)
df.loc[df["EducationLevel"] == "Not Listed", "EducationLevel"] = "N/A"


# -----FOLIUM SET UP-----

color_map = {
    "N/A": "gray",
    "High School": "green",
    "Associate": "purple",
    "Bachelor": "blue",
    "Master": "orange",
    "Doctorate": "red"
}

for idx, row in df.iterrows():
    marker_color = color_map.get(row["EducationLevel"], "gray")
    popup_html = f"""
    <div style="width:200px;">
        <b>{row["PositionTitle"]}</b><br>
        Education: <span style="color:{marker_color};">{row["EducationLevel"]}</span><br>
        Real Salary: ${row["real_salary"]:,.2f}
    </div>
    """
    
    folium.Marker(
        location=[row["lat"], row["lon"]],
        tooltip=row["PositionTitle"],
        popup=folium.Popup(popup_html, width=200),
        icon=folium.Icon(color=marker_color, icon="info-sign")
    ).add_to(m)

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
map_path = OUTPUT_DIR / "int_map.html"
fig.save(map_path)