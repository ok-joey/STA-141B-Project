import pandas as pd
import openpyxl
from jobsbycity import get_all_usajobs
from obtain_msa import map_city_to_county_to_msa

from clean_location import clean_location2
from salary import extract_salary
from salary import attach_rpp
from salary import compute_real_salary
from checkmsa import check_msa_format
from great_tables import GT, style
from great_tables import loc as locations
from sorted import get_avg_real_salary_by_education
from sorted import create_education_salary_table

from pathlib import Path

# for reproducability, go to the USAJOBS API and
# change to your own custom api key and user agent
api_key = "q2xAsevtpdw4xjglLAwkTtOqqFc5NDH8rAbWhc68HUY="
user_agent = "eliseligman20@gmail.com"


def final_data(api_key):
    # reproducable paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_PATH1 = BASE_DIR / "data" / "uscities.csv"
    DATA_PATH2 = BASE_DIR / "data" / "qcew-county-msa-csa-crosswalk.xlsx"
    DATA_PATH3 = BASE_DIR / "data" / "RPPtable.xlsx"

    cities_csv_path = pd.read_csv(DATA_PATH1)
    crosswalk_xlsx_path = pd.read_csv(DATA_PATH2)
    rpp = pd.read_csv(DATA_PATH3)
    

    jobs_df = get_all_usajobs(api_key, user_agent)
    jobs_df[['job_city', 'job_state']] = jobs_df['Locations'].apply(
        lambda x: pd.Series(clean_location2(x))
    )

    jobs_with_msa = map_city_to_county_to_msa(jobs_df, cities_csv_path, crosswalk_xlsx_path)
    jobs_with_msa = extract_salary(jobs_with_msa)
    jobs_with_msa = attach_rpp(jobs_with_msa, rpp_path=rpp)
    jobs_with_msa = compute_real_salary(jobs_with_msa)
    
    df = jobs_with_msa

    return df

# used to create our visual on salary by education level
def education_visual(df):
    education_data = get_avg_real_salary_by_education(df)
    education_gt = create_education_salary_table(education_data)
    education_gt.save("/Users/eliseligman/Downloads/STA141B_FinalProject_education_levels.pdf")



