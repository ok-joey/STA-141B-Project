import pandas as pd

def extract_salary(df):
    """
    Uses the already computed annual average salary column
    (AvgSalaryAnn) to set the final 'annual_salary' column.
    This avoids re-running the annualization logic.
    """
    # Directly use the column already calculated based on HR/DY/MO
    # from the USAJOBS API data.
    df["annual_salary"] = df["AvgSalaryAnn"]
    
    # Ensure the column is a float type for subsequent math
    df["annual_salary"] = df["annual_salary"].astype(float) 

    return df

def attach_rpp(jobs_df, rpp_path):
    """
    After you run map_city_to_county_to_msa(), your jobs_df contains:
       - MSA (from CBSA Code)
    This attaches RPP values based on that MSA code.
    """

    # Load RPP (header is row 6 header=5)
    rpp = pd.read_excel(rpp_path, header=5)

    print("\nRPP columns:", rpp.columns.tolist(), "\n")

    # Clean the RPP dataframe
    rpp.columns = rpp.columns.str.strip()

    # Rename to standard naming
    rpp = rpp.rename(columns={
        "GeoFips": "MSA",
        "2023": "rpp"
    })

    # Standardize MSA codes to 5-digit strings
    rpp["MSA"] = rpp["MSA"].astype(str).str.zfill(5)

    # Standardize MSA codes in jobs_df too
    if "MSA" in jobs_df.columns:
        jobs_df["MSA"] = jobs_df["MSA"].astype(str).str.zfill(5)
    else:
        print("jobs_df does not contain an MSA column.")

    # Merge in the RPP data
    merged = jobs_df.merge(
        rpp[["MSA", "rpp"]],
        on="MSA",
        how="left"
    )

    return merged


def compute_real_salary(df):
    """
    Converts nominal salary → real salary using RPP.
    """
    # If RPP is missing, fallback to mean
    df["rpp_filled"] = df["rpp"].fillna(df["rpp"].mean())

    # Real salary = adjust for cost-of-living
    df["real_salary"] = df["annual_salary"] / (df["rpp_filled"] / 100)

    # Normalize for easier comparison
    national_avg = df["real_salary"].mean()
    df["real_salary_index"] = df["real_salary"] / national_avg

    return df
