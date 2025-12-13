import requests
import pandas as pd
import time

def annualize_salary(min_salary, max_salary, rate_interval):
    """
    Convert min/max salary to annual salary based on rate interval.
    Returns min_ann, max_ann, avg_ann
    """
    if min_salary is None or max_salary is None:
        return None, None, None

    factor = 1
    if rate_interval == "PH":   # hourly
        factor = 40 * 52       # 40 hours/week * 52 weeks
    elif rate_interval == "DY": # daily
        factor = 5 * 52        # 5 days/week * 52 weeks
    elif rate_interval == "MO": # monthly
        factor = 12            # 12 months/year

    min_ann = min_salary * factor
    max_ann = max_salary * factor
    avg_ann = (min_ann + max_ann) / 2
    return min_ann, max_ann, avg_ann

def classify_education(txt):
    '''
    Classify education level from text.
    '''
    t = str(txt).lower()
    if "ph.d" in t or "doctorate" in t:
        return "Doctorate"
    if "master" in t:
        return "Master"
    if "bachelor" in t or "undergraduate" in t:
        return "Bachelor"
    if "associate" in t:
        return "Associate"
    if "high school" in t or "hs diploma" in t:
        return "High School"
    return "Not Listed"

def get_all_usajobs(api_key, user_agent, results_per_page=500, delay=1):
    """
    Fetch all USAJOBS without filters, returning a DataFrame with location info,
    salaries, and now education requirements.
    """


    headers = {
        "Authorization-Key": api_key,
        "User-Agent": user_agent
    }
    start_time = time.time()

    # Get total results
    url = f"https://data.usajobs.gov/api/Search?ResultsPerPage=1&Page=1&WhoMayApply=public&Fields=full"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    total_results = int(data['SearchResult']['SearchResultCountAll'])
    total_pages = (total_results + results_per_page - 1) // results_per_page
    print(f"Total jobs to fetch: {total_results}, pages: {total_pages}")

    all_jobs = []
    # Loop through pages
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

            # Extract salary info
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

            min_ann, max_ann, avg_ann = annualize_salary(min_salary, max_salary, rate_interval)

            # Extract education info
            qualification = descriptor.get("QualificationSummary", "")

            user_area = descriptor.get("UserArea", {}).get("Details", {})
            education_req = user_area.get("Education", "") or user_area.get("EducationRequirements", "")
            education_summary = user_area.get("EducationSummary", "")
            # Build job record
            job = {
                "PositionTitle": descriptor.get('PositionTitle'),
                "OrganizationName": descriptor.get('OrganizationName'),
                "JobCategory": descriptor.get('JobCategory', [{}])[0].get('Name'),
                "Locations": ", ".join(location_names),
                "State": ", ".join([name.split(",")[1].strip() if "," in name else "N/A" for name in location_names]),
                "ApplyURL": descriptor.get('PositionURI'),

                # Salary
                "MinSalary": min_salary,
                "MaxSalary": max_salary,
                "SalaryInterval": rate_interval,
                "MinSalaryAnn": min_ann,
                "MaxSalaryAnn": max_ann,
                "AvgSalaryAnn": avg_ann,

                # education fields
                "QualificationSummary": qualification,
                "EducationRequirements": education_req,
                "EducationSummary": education_summary
            }

            all_jobs.append(job)
        #progress checks
        elapsed_total = time.time() - start_time
        print(f"Elapsed time: {elapsed_total:.2f}s | Fetched page {page}/{total_pages}")
        time.sleep(delay)

    df = pd.DataFrame(all_jobs)
    df["EducationLevel"] = df["QualificationSummary"].apply(classify_education)
    df_sorted = df.sort_values(by='State').reset_index(drop=True)
    return df_sorted


