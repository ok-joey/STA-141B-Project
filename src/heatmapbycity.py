import pandas as pd
import plotly.express as px
from jobsbycity import get_all_usajobs
import os 

from pathlib import Path

# CHANGE TO YOUR OWN API KEY
api_key = "q2xAsevtpdw4xjglLAwkTtOqqFc5NDH8rAbWhc68HUY="

df_sorted = get_all_usajobs(api_key)

# --- Step 1: Split Locations into City and State ---
df_sorted[['City', 'State']] = df_sorted['Locations'].str.split(pat=',', n=1, expand=True)
df_sorted['City'] = df_sorted['City'].str.strip()
df_sorted['State'] = df_sorted['State'].str.strip()

# Step 1: Count jobs per city
# Step 2: Load US cities CSV with coordinates
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH1 = BASE_DIR / "data" / "uscities.csv"
cities_df = pd.read_csv(DATA_PATH1)
cities_df = cities_df.rename(columns={'city': 'City', 'state_id': 'StateAbbrev', 'lat': 'lat', 'lng': 'lon'})
city_counts = df_sorted.groupby(['City', 'State']).size().reset_index(name='JobCount')

# Step 3: Map state names in jobs data to abbreviations
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
city_counts['StateAbbrev'] = city_counts['State'].map(us_state_abbrev)

# Step 4: Merge city_counts with coordinates
city_counts = pd.merge(
    city_counts,
    cities_df[['City', 'StateAbbrev', 'lat', 'lon']],
    on=['City', 'StateAbbrev'],
    how='left'
)

# Optional: Drop cities without coordinates
city_counts = city_counts.dropna(subset=['lat','lon'])

# Step 5: Plot interactive city-level map
fig = px.scatter_geo(
    city_counts,
    lat='lat',
    lon='lon',
    size='JobCount',
    hover_name='City',
    hover_data={'State': True, 'JobCount': True, 'lat': False, 'lon': False},
    scope='usa',
    projection='albers usa',
    title='USAJOBS Count by City'
)

# Step 6: Save and show
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
map_path = OUTPUT_DIR / "usa_jobs_by_city.html"
fig.write_html(map_path)
fig.show()