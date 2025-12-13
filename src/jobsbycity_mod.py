## i updated this file and added a few things in order to do for_prob_2_jobsearch.py

import requests
import pandas as pd
import time

def classify_education(qualification_text):
    """classify education level from job qualification text"""
    if pd.isna(qualification_text) or not isinstance(qualification_text, str):
        return 'Unknown'
    
    text = qualification_text.lower()
    
    # check for phd first (most specific)
    if any(term in text for term in ['ph.d', 'phd', 'doctorate', 'doctoral degree', 'doctor of']):
        return 'PhD'
    
    # then masters
    if any(term in text for term in ['master', "master's", 'm.s.', 'm.a.', 'mba', 'm.ed']):
        return 'Masters'
    
    # then bachelors
    if any(term in text for term in ['bachelor', "bachelor's", 'b.s.', 'b.a.', 'baccalaureate', '4-year degree', 'four-year degree']):
        return 'Bachelors'
    
    # then associates
    if any(term in text for term in ['associate', "associate's", 'a.a.', 'a.s.', '2-year degree', 'two-year degree']):
        return 'Associates'
    
    # then high school
    if any(term in text for term in ['high school', 'hs diploma', 'ged', 'secondary education']):
        return 'High School'
    
    # no education required
    if any(term in text for term in ['no education', 'education not required', 'no degree']):
        return 'None'
    
    return 'Unknown'

def annualize_salary(min_salary, max_salary, rate_interval):
    """convert salary to annual amounts based on payment interval"""
    if min_salary is None or max_salary is None:
        return None, None, None

    factor = 1
    if rate_interval == "HR":
        factor = 40 * 52  # hourly to annual
    elif rate_interval == "DY":
        factor = 5 * 52   # daily to annual
    elif rate_interval == "MO":
        factor = 12       # monthly to annual

    min_ann = min_salary * factor
    max_ann = max_salary * factor
    avg_ann = (min_ann + max_ann) / 2
    return min_ann, max_ann, avg_ann

def get_all_usajobs(api_key, results_per_page=500, delay=1):
    """fetch all usajobs postings via API and add education classification"""
    headers = {
        "Authorization-Key": api_key,
        "User-Agent": "edherrera@ucdavis.edu"
    }
    start_time = time.time()

    # first request to get total count
    url = f"https://data.usajobs.gov/api/Search?ResultsPerPage=1&Page=1&WhoMayApply=public&Fields=full"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    total_results = int(data['SearchResult']['SearchResultCountAll'])
    total_pages = (total_results + results_per_page - 1) // results_per_page
    print(f"Total jobs to fetch: {total_results}, pages: {total_pages}")

    all_jobs = []

    # loop through all pages
    for page in range(1, total_pages + 1):
        url = f"https://data.usajobs.gov/api/Search?ResultsPerPage={results_per_page}&Page={page}&WhoMayApply=public&Fields=full"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Warning: page {page} failed with status {resp.status_code}")
            continue

        page_data = resp.json()
        for item in page_data['SearchResult']['SearchResultItems']:
            descriptor = item['MatchedObjectDescriptor']
            locations = descriptor.get('PositionLocation', [])
            location_names = [loc.get('LocationName', 'N/A') for loc in locations]

            # get salary info
            remuneration_list = descriptor.get('PositionRemuneration', [])
            min_salary = None
            max_salary = None
            rate_interval = None

            for rem in remuneration_list:
                try:
                    min_candidate = float(rem.get('MinimumRange', None))
                    max_candidate = float(rem.get('MaximumRange', None))
                    if min_candidate is not None and max_candidate is not None:
                        min_salary = min_candidate
                        max_salary = max_candidate
                        rate_interval = rem.get('RateIntervalCode')
                        break
                except (TypeError, ValueError):
                    continue

            # annualize salaries
            min_ann, max_ann, avg_ann = annualize_salary(min_salary, max_salary, rate_interval)
            
            # classify education level
            qualification_summary = descriptor.get('QualificationSummary', '')
            education_level = classify_education(qualification_summary)

            job = {
                "PositionTitle": descriptor.get('PositionTitle'),
                "OrganizationName": descriptor.get('OrganizationName'),
                "JobCategory": descriptor.get('JobCategory', [{}])[0].get('Name'),
                "Locations": ", ".join(location_names),
                "State": ", ".join([name.split(",")[1].strip() if "," in name else "N/A" for name in location_names]),
                "ApplyURL": descriptor.get('PositionURI'),
                "MinSalary": min_salary,
                "MaxSalary": max_salary,
                "SalaryInterval": rate_interval,
                "MinSalaryAnn": min_ann,
                "MaxSalaryAnn": max_ann,
                "AvgSalaryAnn": avg_ann,
                "QualificationSummary": qualification_summary,
                "EducationLevel": education_level
            }
            all_jobs.append(job)

        elapsed_total = time.time() - start_time
        print(f"Elapsed time: {elapsed_total:.2f}s | Fetched page {page}/{total_pages}")
        time.sleep(delay)

    df = pd.DataFrame(all_jobs)
    df_sorted = df.sort_values(by='State').reset_index(drop=True)
    return df_sorted
