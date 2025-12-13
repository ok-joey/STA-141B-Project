# calculations for question 3 - education and salary stats
# shows job counts and salary stats by education level

import pandas as pd
import numpy as np

# load the data
jobs_df = pd.read_excel('/Users/edgarherrera8/Desktop/Cursor/FINAL_PROJECT/STA141B Final Project/STA141B_FinalProject_jobs.xlsx')

print("="*80)
print("RESEARCH QUESTION 3: EDUCATION OPPORTUNITIES")
print("="*80)
print()

# basic stats
total_jobs = len(jobs_df)
jobs_with_education = jobs_df['EducationLevel'].notna().sum()

print(f"Total jobs in dataset: {total_jobs:,}")
print(f"Jobs with EducationLevel assigned: {jobs_with_education:,}")
print(f"Jobs without EducationLevel: {total_jobs - jobs_with_education:,}")
print()

# use real_salary if available, otherwise annual_salary
salary_col = 'real_salary' if 'real_salary' in jobs_df.columns else 'annual_salary'
print(f"Using salary column: {salary_col}")
print()

# table 1: job count by education level
print("="*80)
print("TABLE 1: Job Count by Education Level")
print("="*80)

education_counts = jobs_df['EducationLevel'].value_counts().reset_index()
education_counts.columns = ['EducationLevel', 'Count']
education_counts['Percentage'] = (education_counts['Count'] / total_jobs * 100).round(2)
education_counts = education_counts.sort_values('Count', ascending=False)

for _, row in education_counts.iterrows():
    print(f"{row['EducationLevel']:15s}: {row['Count']:5,} jobs ({row['Percentage']:5.2f}%)")

print()

# table 2: salary stats by education level
print("="*80)
print("TABLE 2: Salary Statistics by Education Level")
print("="*80)

salary_stats = jobs_df.groupby('EducationLevel')[salary_col].agg([
    ('Count', 'count'),
    ('Mean', 'mean'),
    ('Median', 'median'),
    ('Min', 'min'),
    ('Max', 'max')
]).reset_index()

salary_stats = salary_stats.sort_values('Mean', ascending=False)

print(f"{'Education Level':<15} {'Count':<8} {'Mean Salary':<15} {'Median Salary':<15} {'Min':<12} {'Max':<12}")
print("-" * 80)

for _, row in salary_stats.iterrows():
    print(f"{row['EducationLevel']:<15} {row['Count']:<8,} ${row['Mean']:<14,.2f} ${row['Median']:<14,.2f} ${row['Min']:<11,.2f} ${row['Max']:<11,.2f}")

print()

# key findings
print("="*80)
print("KEY FINDINGS")
print("="*80)

# highest and lowest salaries
highest_edu = salary_stats.loc[salary_stats['Mean'].idxmax()]
lowest_edu = salary_stats.loc[salary_stats['Mean'].idxmin()]

print(f"Highest average salary: {highest_edu['EducationLevel']} = ${highest_edu['Mean']:,.2f}")
print(f"Lowest average salary: {lowest_edu['EducationLevel']} = ${lowest_edu['Mean']:,.2f}")
print()

# associates vs bachelors comparison
associates_mean = jobs_df[jobs_df['EducationLevel'] == 'Associates'][salary_col].mean()
bachelors_mean = jobs_df[jobs_df['EducationLevel'] == 'Bachelors'][salary_col].mean()
difference = associates_mean - bachelors_mean

print("Associates vs Bachelors Comparison:")
print(f"  Associates mean salary: ${associates_mean:,.2f}")
print(f"  Bachelors mean salary: ${bachelors_mean:,.2f}")
print(f"  Difference: ${difference:,.2f}")
print(f"  Associates earns ${difference:,.2f} more than Bachelors")
print()

# unknown category
unknown_mean = jobs_df[jobs_df['EducationLevel'] == 'Unknown'][salary_col].mean()
unknown_count = len(jobs_df[jobs_df['EducationLevel'] == 'Unknown'])
unknown_percentage = (unknown_count / total_jobs * 100)

print("Unknown Education Level Analysis:")
print(f"  Count: {unknown_count:,} jobs ({unknown_percentage:.2f}% of total)")
print(f"  Mean salary: ${unknown_mean:,.2f}")
print()

print("="*80)
print("CALCULATIONS COMPLETE")
print("="*80)
