import pandas as pd
import plotly.express as px
from jobsbycity import get_all_usajobs
import os

# data
api_key = "q2xAsevtpdw4xjglLAwkTtOqqFc5NDH8rAbWhc68HUY="
df = get_all_usajobs(api_key)

# Split 'Locations' into 'City' and 'State'
df[['City', 'State']] = df['Locations'].str.split(pat=',', n=1, expand=True)
df['City'] = df['City'].str.strip()
df['State'] = df['State'].str.strip()

# education classifier
def classify_education(txt):
    t = str(txt).lower()
    if "master" in t:
        return "Master"
    if "bachelor" in t or "undergraduate" in t:
        return "Bachelor"
    if "associate" in t:
        return "Associate"
    if "high school" in t or "hs diploma" in t:
        return "High School"
    if "ph.d" in t or "doctorate" in t:
        return "Doctorate"
    return "Not Listed"

df["EducationLevel"] = df["QualificationSummary"].apply(classify_education)

# city coordinates
cities_df = pd.read_csv(r"/Users/eliseligman/Downloads/uscities.csv")
cities_df = cities_df.rename(columns={
    'city': 'City',
    'state_id': 'StateAbbrev',
    'lat': 'lat',
    'lng': 'lon'
})

# state name to abbrev mapping
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

df['StateAbbrev'] = df['State'].map(us_state_abbrev)

# merge to add lat and lon
df = df.merge(
    cities_df[['City', 'StateAbbrev', 'lat', 'lon']],
    on=['City', 'StateAbbrev'],
    how='left'
)

# Drop rows with unknown coordinates (these are unusable for mapping)
df = df.dropna(subset=['lat', 'lon'])

# heatmap functions
def heatmap_by_city_education(df):
    df_clean = df.dropna(subset=['EducationLevel'])
    fig = px.scatter_geo(
        df_clean,
        lat='lat',
        lon='lon',
        color='EducationLevel',
        hover_name='City',
        scope='usa',
        projection='albers usa',
        title='Education Requirements by City (USAJOBS)'
    )
    fig.write_html("/Users/eliseligman/Downloads/heatmap_education_all.html")
    fig.show()

# heatmap only not listed to bachelor
allowed_lvls = ["Not Listed", "High School", "Associate", "Bachelor"]

def heatmap_limited_education(df):
    df_small = df[df['EducationLevel'].isin(allowed_lvls)]
    fig = px.scatter_geo(
        df_small,
        lat='lat',
        lon='lon',
        color='EducationLevel',
        hover_name='City',
        scope='usa',
        projection='albers usa',
        title='Education Requirements (≤ Bachelor)'
    )
    fig.write_html("/Users/eliseligman/Downloads/heatmap_education_limited.html")
    fig.show()

heatmap_by_city_education(df)
heatmap_limited_education(df)
