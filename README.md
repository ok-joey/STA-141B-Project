# Federal Job Market Analysis & Search Tool

An interactive analysis of ~8,000 federal job postings from [USAJOBS](https://developer.usajobs.gov/), built for STA 141B (UC Davis, Fall 2025).

## Essential Questions
1. What is the geographic distribution of federal job postings by state?
2. How do education requirements relate to location and salary?
3. How can we help a user find the highest-paying and nearest federal jobs based on their location and qualifications?

## What We Built
- **Data pipeline:** collects postings from the USAJOBS API, cleans location data, and adds coordinates and a cost-of-living adjustment so salaries are comparable across regions.
- **Cost-of-living-adjusted salaries:** postings are matched to Metropolitan Statistical Areas and merged with Regional Price Parity (RPP) data to produce a "real salary."
- **Interactive maps:** scatter maps of job counts and education requirements, plus a final Folium map with color-coded markers (by required education level) and click-through popups showing position title, education level, and real salary.
- **Job search tool:** filters postings by education level, salary, and distance from a chosen city, and sorts by highest real salary or nearest distance.
<img width="866" height="668" alt="Screenshot 2026-10-03 132059" src="https://github.com/user-attachments/assets/e8ef7484-74cd-4df1-9224-fc9d165daa3b" />


## Key Findings
- Federal postings are concentrated in the eastern half of the U.S. and around the Washington, D.C. area, with fewer in states like Nevada, Montana, and Idaho.
- Cost-of-living adjustment changes how salaries compare across regions, which is why we report real salary rather than nominal salary.
- Average real salary generally rises with education level, with some exceptions (for example, Associate-level postings average higher than Bachelor's in this dataset, possibly because of how education levels are listed or because the roles are more specialized).

## Data Sources
- [USAJOBS API](https://developer.usajobs.gov/): job postings
- [SimpleMaps US Cities Database](https://simplemaps.com/data/us-cities): city coordinates and FIPS codes
- [BLS QCEW county-MSA-CSA crosswalk](https://www.bls.gov/cew/classifications/areas/county-msa-csa-crosswalk.html): maps counties to MSAs
- [BEA Regional Price Parity](https://apps.bea.gov/): cost-of-living adjustment

We first tried the Geocodio API for coordinates but its free tier (2,500 lookups/day) was too small for 8,000+ postings, so we merged public datasets instead.

## Repository Structure
```
data/      Input datasets and cleaned data
src/       Python scripts for the pipeline, maps, and search tool
outputs/   Generated .html maps and visualizations
```

## Limitations
- Only federal postings, so the results don't represent the whole job market.
- Jobs are placed at city centroids, so postings within one city all appear at the same point.
- Data is a snapshot from March 2026; postings change constantly.

## Team
Edgar Herrera, Madeline Iwami, Eli Seligman, and Joey Suen, with instructor Professor Nicolai Amann.

**My role (Joey):** built the interactive front end (Folium map with color-coded markers and HTML/CSS popups) and contributed to USAJOBS API data collection.

## Report
Full write-up: [`STA141B_Final_Project.pdf`](STA141B_Final_Project.pdf)
