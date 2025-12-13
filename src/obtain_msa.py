def map_city_to_county_to_msa(jobs_df, cities_csv_path, crosswalk_xlsx_path):
    import pandas as pd

    # Load USCities dataset
    cities_df = pd.read_csv(cities_csv_path)[
        ['city', 'state_id', 'state_name', 'county_fips', 'county_name']
    ]
    cities_df['city'] = cities_df['city'].str.lower()

    # Load Crosswalk with county → MSA codes
    county_to_msa_df = pd.read_excel(
        crosswalk_xlsx_path,
        sheet_name='Jul. 2023 Crosswalk',
        dtype=str
    )[
        ['County Code', 'County Title', 'MSA Code', 'MSA Title']
    ]

    county_to_msa_df['County Code'] = county_to_msa_df['County Code'].astype(int)

    # Split "Locations" → city + state
    def split_city_state(location):
        if pd.isna(location):
            return pd.Series([None, None])
        parts = location.split(',')
        if len(parts) < 2:
            return pd.Series([None, None])
        return pd.Series([parts[0].strip().lower(), parts[1].strip()])

    jobs_df[['job_city', 'job_state']] = jobs_df['Locations'].apply(split_city_state)

    # Map full state names → abbreviations
    state_map = dict(zip(cities_df['state_name'], cities_df['state_id']))
    jobs_df['job_state_id'] = jobs_df['job_state'].map(state_map)

    # Merge jobs → cities
    merged_df = jobs_df.merge(
        cities_df,
        how='left',
        left_on=['job_city', 'job_state_id'],
        right_on=['city', 'state_id']
    )

    # Convert county_fips to int for matching
    merged_df['county_fips'] = merged_df['county_fips'].astype(float).astype('Int64')

    # Merge in the MSA crosswalk
    merged_df = merged_df.merge(
        county_to_msa_df,
        how='left',
        left_on='county_fips',
        right_on='County Code'
    )
    # Remove "C" prefix
    merged_df['MSA'] = merged_df['MSA Code'].astype(str).str.replace("C", "")

    # Add a trailing 0
    merged_df['MSA'] = merged_df['MSA'] + "0"

    # Ensure 5 digits (just in case)
    merged_df['MSA'] = merged_df['MSA'].str.zfill(5)


    return merged_df
