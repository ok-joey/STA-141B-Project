import pandas as pd
import numpy as np
import re
from geopy.distance import geodesic
import plotly.graph_objects as go
from typing import Optional, Tuple

# interactive job search tool for question 4
# lets users search for jobs by location, education level, and sort by salary or distance

def get_city_coordinates(city: str, state: str, cities_df: pd.DataFrame) -> Optional[Tuple[float, float]]:
    """get lat/lon for a city and state"""
    city_lower = city.lower().strip()
    state_upper = state.upper().strip()
    
    # try exact match first
    match = cities_df[
        (cities_df['city'].str.lower() == city_lower) & 
        (cities_df['state_id'] == state_upper)
    ]
    
    if len(match) > 0:
        return (match.iloc[0]['lat'], match.iloc[0]['lng'])
    
    # try partial match if exact doesn't work
    match = cities_df[
        (cities_df['city'].str.lower().str.contains(city_lower, na=False, regex=False)) & 
        (cities_df['state_id'] == state_upper)
    ]
    
    if len(match) > 0:
        return (match.iloc[0]['lat'], match.iloc[0]['lng'])
    
    return None

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """calculate distance in miles between two coordinates using geodesic distance"""
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return np.nan
    return geodesic((lat1, lon1), (lat2, lon2)).miles

def parse_city_state_from_locations(locations_str: str) -> Optional[Tuple[str, str]]:
    """parse city and state from the Locations field, used as fallback when job_city is wrong"""
    if pd.isna(locations_str) or not locations_str:
        return None
    
    locations_str = str(locations_str)
    
    # state abbreviations
    state_map = {
        'california': 'CA', 'texas': 'TX', 'florida': 'FL', 'new york': 'NY',
        'pennsylvania': 'PA', 'illinois': 'IL', 'ohio': 'OH', 'georgia': 'GA',
        'north carolina': 'NC', 'michigan': 'MI', 'new jersey': 'NJ', 'virginia': 'VA',
        'washington': 'WA', 'arizona': 'AZ', 'massachusetts': 'MA', 'tennessee': 'TN',
        'indiana': 'IN', 'missouri': 'MO', 'maryland': 'MD', 'wisconsin': 'WI',
        'colorado': 'CO', 'minnesota': 'MN', 'south carolina': 'SC', 'alabama': 'AL',
        'louisiana': 'LA', 'kentucky': 'KY', 'oregon': 'OR', 'oklahoma': 'OK',
        'connecticut': 'CT', 'utah': 'UT', 'iowa': 'IA', 'nevada': 'NV',
        'arkansas': 'AR', 'mississippi': 'MS', 'kansas': 'KS', 'new mexico': 'NM',
        'nebraska': 'NE', 'west virginia': 'WV', 'idaho': 'ID', 'hawaii': 'HI',
        'new hampshire': 'NH', 'maine': 'ME', 'montana': 'MT', 'rhode island': 'RI',
        'delaware': 'DE', 'south dakota': 'SD', 'north dakota': 'ND', 'alaska': 'AK',
        'vermont': 'VT', 'wyoming': 'WY', 'district of columbia': 'DC'
    }
    
    # if california is in the string, try to find a california city first
    if 'california' in locations_str.lower() or ', CA' in locations_str.upper():
        pattern = r'([A-Za-z\s]+?),\s*(California|CA)'
        matches = re.findall(pattern, locations_str, re.IGNORECASE)
        if matches:
            city = matches[0][0].strip()
            return (city, 'CA')
    
    # general pattern to find any city, state pair
    pattern = r'([A-Za-z\s]+?),\s*([A-Za-z\s]+?)(?:,|$)'
    matches = re.findall(pattern, locations_str)
    
    for city, state_str in matches:
        city = city.strip()
        state_str = state_str.strip().lower()
        
        if state_str in state_map:
            return (city, state_map[state_str])
        elif state_str.upper() in state_map.values():
            return (city, state_str.upper())
    
    return None

def search_jobs(
    jobs_df: pd.DataFrame,
    cities_df: pd.DataFrame,
    user_city: str,
    user_state: str,
    max_results: int = 20,
    sort_by: str = 'salary',
    max_distance: Optional[float] = None,
    education_level: Optional[str] = None
) -> pd.DataFrame:
    """main search function - filters by education, calculates distances, sorts results"""
    filtered_df = jobs_df.copy()
    
    # filter by education if specified
    if education_level and education_level.strip():
        if 'EducationLevel' in jobs_df.columns:
            filtered_df = filtered_df[filtered_df['EducationLevel'].str.lower() == education_level.lower()].copy()
            print(f"Filtered to {len(filtered_df)} jobs matching education level: {education_level}")
        else:
            print("Warning: EducationLevel column not found. Searching all jobs.")
    
    # get user location coordinates
    user_coords = get_city_coordinates(user_city, user_state, cities_df)
    if user_coords is None:
        raise ValueError(f"Could not find coordinates for {user_city}, {user_state}")
    
    user_lat, user_lon = user_coords
    print(f"User location: {user_city}, {user_state} ({user_lat:.4f}, {user_lon:.4f})")
    
    filtered_df['job_lat'] = None
    filtered_df['job_lon'] = None
    filtered_df['distance_miles'] = np.nan
    
    # calculate distance to each job
    for idx, row in filtered_df.iterrows():
        # try using job_city and job_state_id first
        job_coords = get_city_coordinates(
            str(row.get('job_city', '')),
            str(row.get('job_state_id', '')),
            cities_df
        )
        
        # if that doesn't work, parse from Locations field
        # this handles cases where job_city is wrong (like san francisco jobs showing as mobile, al)
        if not job_coords and 'Locations' in row:
            locations_str = str(row.get('Locations', ''))
            
            # find all city-state pairs in the locations string
            pattern = r'([A-Za-z\s]+?),\s*([A-Za-z\s]+?)(?:,|$)'
            matches = re.findall(pattern, locations_str)
            
            state_map = {
                'california': 'CA', 'texas': 'TX', 'florida': 'FL', 'new york': 'NY',
                'pennsylvania': 'PA', 'illinois': 'IL', 'ohio': 'OH', 'georgia': 'GA',
                'north carolina': 'NC', 'michigan': 'MI', 'new jersey': 'NJ', 'virginia': 'VA',
                'washington': 'WA', 'arizona': 'AZ', 'massachusetts': 'MA', 'tennessee': 'TN',
                'indiana': 'IN', 'missouri': 'MO', 'maryland': 'MD', 'wisconsin': 'WI',
                'colorado': 'CO', 'minnesota': 'MN', 'south carolina': 'SC', 'alabama': 'AL',
                'louisiana': 'LA', 'kentucky': 'KY', 'oregon': 'OR', 'oklahoma': 'OK',
                'connecticut': 'CT', 'utah': 'UT', 'iowa': 'IA', 'nevada': 'NV',
                'arkansas': 'AR', 'mississippi': 'MS', 'kansas': 'KS', 'new mexico': 'NM',
                'nebraska': 'NE', 'west virginia': 'WV', 'idaho': 'ID', 'hawaii': 'HI',
                'new hampshire': 'NH', 'maine': 'ME', 'montana': 'MT', 'rhode island': 'RI',
                'delaware': 'DE', 'south dakota': 'SD', 'north dakota': 'ND', 'alaska': 'AK',
                'vermont': 'VT', 'wyoming': 'WY', 'district of columbia': 'DC'
            }
            
            best_coords = None
            best_distance = float('inf')
            
            # try each city and pick the one closest to user (or within distance limit)
            for city, state_str in matches:
                city = city.strip()
                state_str = state_str.strip().lower()
                
                if state_str in state_map:
                    state_abbrev = state_map[state_str]
                elif state_str.upper() in state_map.values():
                    state_abbrev = state_str.upper()
                else:
                    continue
                
                test_coords = get_city_coordinates(city, state_abbrev, cities_df)
                if test_coords:
                    test_dist = calculate_distance(user_lat, user_lon, test_coords[0], test_coords[1])
                    
                    # prefer cities within distance limit if specified
                    if max_distance is not None:
                        if test_dist <= max_distance:
                            if test_dist < best_distance:
                                best_coords = test_coords
                                best_distance = test_dist
                    else:
                        # no distance limit, just pick closest
                        if test_dist < best_distance:
                            best_coords = test_coords
                            best_distance = test_dist
            
            if best_coords:
                job_coords = best_coords
        
        if job_coords:
            filtered_df.at[idx, 'job_lat'] = job_coords[0]
            filtered_df.at[idx, 'job_lon'] = job_coords[1]
            filtered_df.at[idx, 'distance_miles'] = calculate_distance(
                user_lat, user_lon, job_coords[0], job_coords[1]
            )
    
    # remove jobs without coordinates
    filtered_df = filtered_df.dropna(subset=['job_lat', 'job_lon'])
    
    # filter by max distance if specified
    if max_distance is not None:
        filtered_df = filtered_df[filtered_df['distance_miles'] <= max_distance]
        print(f"Filtered to jobs within {max_distance} miles: {len(filtered_df)} jobs remaining")
    
    # sort results
    if sort_by == 'salary':
        salary_col = 'real_salary' if 'real_salary' in filtered_df.columns else 'annual_salary'
        filtered_df = filtered_df.sort_values(by=salary_col, ascending=False, na_position='last')
        print(f"Sorted by {salary_col} (highest first)")
    elif sort_by == 'distance':
        filtered_df = filtered_df.sort_values(by='distance_miles', ascending=True, na_position='last')
        print(f"Sorted by distance (nearest first)")
    
    result_df = filtered_df.head(max_results).copy()
    
    # set up output columns
    output_cols = ['PositionTitle', 'OrganizationName', 'Locations', 'annual_salary', 'distance_miles']
    if 'real_salary' in result_df.columns:
        output_cols.insert(4, 'real_salary')
    if 'EducationLevel' in result_df.columns:
        output_cols.insert(3, 'EducationLevel')
    if 'ApplyURL' in result_df.columns:
        output_cols.append('ApplyURL')
    
    # include coordinates for map creation
    result_output = result_df[output_cols].copy()
    if 'job_lat' in result_df.columns and 'job_lon' in result_df.columns:
        result_output['job_lat'] = result_df['job_lat'].values
        result_output['job_lon'] = result_df['job_lon'].values
    
    return result_output

def create_job_map(
    jobs_df: pd.DataFrame,
    user_city: str,
    user_state: str,
    cities_df: pd.DataFrame,
    output_path: Optional[str] = None
):
    """create interactive map showing jobs and user location"""
    fig = go.Figure()
    
    if len(jobs_df) > 0:
        salary_col = 'real_salary' if 'real_salary' in jobs_df.columns else 'annual_salary'
        
        # scale marker sizes based on salary
        salary_values = jobs_df[salary_col].fillna(0)
        if salary_values.max() > salary_values.min():
            marker_sizes = 5 + (salary_values - salary_values.min()) / (salary_values.max() - salary_values.min()) * 25
        else:
            marker_sizes = 15
        
        # build hover text with job info
        hover_text = jobs_df['PositionTitle'] + '<br>' + \
                     jobs_df['OrganizationName'] + '<br>' + \
                     jobs_df['Locations'].astype(str) + '<br>' + \
                     'Salary: $' + jobs_df[salary_col].astype(int).astype(str)
        
        if 'distance_miles' in jobs_df.columns:
            hover_text += '<br>' + 'Distance: ' + jobs_df['distance_miles'].round(1).astype(str) + ' miles'
        
        # add job markers
        fig.add_trace(go.Scattergeo(
            lat=jobs_df['job_lat'],
            lon=jobs_df['job_lon'],
            mode='markers',
            marker=dict(
                size=marker_sizes,
                color=jobs_df[salary_col],
                colorscale='Viridis',
                colorbar=dict(title="Salary ($)"),
                sizemin=5,
                line=dict(width=1, color='white')
            ),
            text=hover_text,
            hoverinfo='text',
            name='Job Postings'
        ))
    
    # add user location marker (red star)
    user_coords = get_city_coordinates(user_city, user_state, cities_df)
    if user_coords:
        user_lat, user_lon = user_coords
        fig.add_trace(go.Scattergeo(
            lat=[user_lat],
            lon=[user_lon],
            mode='markers',
            marker=dict(
                size=15,
                color='red',
                symbol='star',
                line=dict(width=2, color='white')
            ),
            text=[f'Your Location: {user_city}, {user_state}'],
            hoverinfo='text',
            name='Your Location'
        ))
    
    fig.update_layout(
        title='Job Search Results Map',
        geo=dict(
            scope='usa',
            projection=dict(type='albers usa'),
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        ),
        height=600
    )
    
    if output_path:
        fig.write_html(output_path)
        print(f"Map saved to {output_path}")
        
        # also export as png for report
        png_path = output_path.replace('.html', '.png')
        try:
            fig.write_image(png_path, width=1200, height=800)
            print(f"PNG image saved to {png_path}")
        except Exception as e:
            print(f"Note: PNG export requires 'kaleido' package. Install with: pip3 install kaleido")
            print(f"Error: {e}")
    
    fig.show()
    return fig

def interactive_job_search(
    jobs_file_path: str,
    cities_file_path: str,
    user_city: str,
    user_state: str,
    max_results: int = 20,
    sort_by: str = 'salary',
    show_map: bool = True,
    max_distance: Optional[float] = None,
    education_level: Optional[str] = None
):
    """main function to run the interactive job search"""
    print("Loading job data...")
    jobs_df = pd.read_excel(jobs_file_path)
    
    print("Loading city coordinates...")
    cities_df = pd.read_csv(cities_file_path)
    
    results = search_jobs(
        jobs_df, cities_df, user_city, user_state,
        max_results=max_results, sort_by=sort_by, max_distance=max_distance,
        education_level=education_level
    )
    
    print(f"\n{'='*80}")
    print(f"TOP {len(results)} JOBS")
    print(f"{'='*80}\n")
    print(results.to_string(index=False))
    
    if show_map and len(results) > 0:
        # use coordinates from search if available
        if 'job_lat' in results.columns and 'job_lon' in results.columns:
            results_with_coords = results.dropna(subset=['job_lat', 'job_lon']).copy()
        else:
            # fallback: recalculate coordinates (shouldn't happen usually)
            results_with_coords = results.copy()
            results_with_coords['job_lat'] = None
            results_with_coords['job_lon'] = None
            
            for idx, row in results_with_coords.iterrows():
                job_match = jobs_df[jobs_df['PositionTitle'] == row['PositionTitle']]
                if len(job_match) > 0:
                    job_row = job_match.iloc[0]
                    job_city = job_row.get('job_city', '')
                    job_state = job_row.get('job_state_id', '')
                    coords = get_city_coordinates(str(job_city), str(job_state), cities_df)
                    
                    if not coords and 'Locations' in job_row:
                        parsed = parse_city_state_from_locations(str(job_row.get('Locations', '')))
                        if parsed:
                            city, state = parsed
                            coords = get_city_coordinates(city, state, cities_df)
                    
                    if coords:
                        results_with_coords.at[idx, 'job_lat'] = coords[0]
                        results_with_coords.at[idx, 'job_lon'] = coords[1]
            
            results_with_coords = results_with_coords.dropna(subset=['job_lat', 'job_lon'])
        
        if len(results_with_coords) > 0:
            map_filename = 'job_search_map.html'
            if user_city:
                map_filename = f'job_search_map_{user_city.replace(" ", "_")}.html'
            
            create_job_map(
                results_with_coords,
                user_city, user_state, cities_df,
                output_path=f'/Users/edgarherrera8/Desktop/Cursor/FINAL_PROJECT/STA141B Final Project/{map_filename}'
            )
        else:
            print("Warning: No jobs with valid coordinates found. Cannot create map.")
    
    return results

if __name__ == "__main__":
    jobs_path = '/Users/edgarherrera8/Desktop/Cursor/FINAL_PROJECT/STA141B Final Project/STA141B_FinalProject_jobs.xlsx'
    cities_path = '/Users/edgarherrera8/Desktop/Cursor/FINAL_PROJECT/STA141B Final Project/uscities.csv'
    
    # example 1: all jobs within 100 miles
    results1 = interactive_job_search(
        jobs_file_path=jobs_path,
        cities_file_path=cities_path,
        user_city='Davis',
        user_state='CA',
        max_results=15,
        sort_by='salary',
        show_map=True,
        max_distance=100,
        education_level=None
    )
    
    # example 2: bachelors jobs only
    results2 = interactive_job_search(
        jobs_file_path=jobs_path,
        cities_file_path=cities_path,
        user_city='Davis',
        user_state='CA',
        max_results=15,
        sort_by='salary',
        show_map=True,
        max_distance=100,
        education_level='Bachelors'
    )
