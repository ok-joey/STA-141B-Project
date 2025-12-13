import pandas as pd
from great_tables import GT, style
from great_tables import loc as locations

def get_avg_real_salary_by_education(df):
    """
    Aggregates the real_salary by the 'EducationLevel' column,
    calculates the average real salary for each, and sorts the results.
    
    The input DataFrame is expected to have 'EducationLevel' and 
    'real_salary' columns.
    
    Args:
        df (pd.DataFrame): The job dataset.
        
    Returns:
        pd.DataFrame: A DataFrame with the 'EducationLevel' 
                      and the corresponding 'AvgRealSalary'.
    """
    
    # Fill NaN values in 'EducationLevel' to group them as 'Not Specified'
    # This prevents the aggregation step from silently dropping them.
    df['EducationLevel'] = df['EducationLevel'].fillna('Not Specified')
    
    # 1. Group by 'EducationLevel' and calculate the mean of 'real_salary'
    avg_real_salary_by_education = df.groupby('EducationLevel')['real_salary'].mean()
    
    # 2. Sort the results in descending order (highest average salary first)
    sorted_avg_salary = avg_real_salary_by_education.sort_values(ascending=False)
    
    # Convert the resulting Series to a DataFrame for clear formatting
    education_df = sorted_avg_salary.reset_index()
    education_df.columns = ['EducationLevel', 'AvgRealSalary']
    

    education_df = education_df.sort_values(by='AvgRealSalary', ascending=False)

    return education_df
def create_education_salary_table(data_df):
    """Creates an aesthetically pleasing Great Table for Salary by Education Level."""
    gt_table = (
        GT(data_df)
        .fmt_currency(
            columns='AvgRealSalary',
            currency="USD",
            decimals=0,
        )
        .tab_header(
            title="Average Real Salary vs. Education Level",
            subtitle="Salaries are adjusted for Cost of Living (RPP)"
        )
        .cols_label(
            EducationLevel="Education Level",
            AvgRealSalary="Average Real Salary"
        )
        .data_color( # Color the salary column based on value (Blue for high)
            columns='AvgRealSalary',
            palette="Blues",
            domain=[data_df['AvgRealSalary'].min(), data_df['AvgRealSalary'].max()]
        )
        .tab_source_note(
            source_note="Data based on USAJOBS API and BEA RPP data."
        )
        .tab_options(
            table_font_names=["Arial", "Helvetica", "sans-serif"],
            table_body_hlines_style="none",  # 🔥 FIX FOR HORIZONTAL LINES
            table_body_vlines_style="none"
        )
        .opt_align_table_header(align="left")
    )
    return gt_table
