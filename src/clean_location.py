import pandas as pd
import re

def clean_location2(raw_loc):
    if pd.isna(raw_loc) or not isinstance(raw_loc, str):
        return None, None

    loc = raw_loc.strip()

    # Remove special characters for matching
    clean = re.sub(r"[^a-zA-Z0-9 ]", "", loc).lower()

    #military bases
    military_mapping = {
        "maxwell afb": ("Montgomery", "AL"),
        "gunter afb": ("Montgomery", "AL"),
        "redstone arsenal": ("Huntsville", "AL"),
        "fort rucker": ("Ozark", "AL"),
        "anniston army depot": ("Anniston", "AL"),
        "fort richardson": ("Anchorage", "AK"),
        "fort wainwright": ("Fairbanks", "AK"),
        "elmendorf afb": ("Anchorage", "AK"),
        "eielson afb": ("Fairbanks", "AK"),
    }

    for base in military_mapping:
        if base in clean:
            return military_mapping[base]

    #splits county format
    if "county," in loc.lower():
        parts = loc.split("County,", 1)
        county = parts[0].strip()
        state = normalize_state(parts[1].strip())
        return county, state

    
    parts = [p.strip() for p in loc.split(",")]

    if len(parts) == 2:
        city, state = parts
    elif len(parts) > 2:
        city = parts[0]
        state = parts[-1]
    else:
        return None, None

    return city, normalize_state(state)


def normalize_state(state):
    if state is None:
        return None

    state = state.strip()

    us_state_abbrev = {
        'Alabama': 'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
        'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
        'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
        'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA',
        'Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT',
        'Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
        'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
        'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD',
        'Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
        'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'
    }

    # Already two-letter code
    if len(state) == 2 and state.isalpha():
        return state.upper()

    return us_state_abbrev.get(state, None)
