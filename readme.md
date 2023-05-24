# DC School Lottery Data Dashboard

This repository contains two main Python scripts (`cleaning_data.py` and `app.py`) for cleaning data and making a Shiny dashboard application that visualizes the DC lottery data for the 2023-2024 school year.

## Data Cleaning (`cleaning_data.py`)

"""
The script `cleaning_data.py` performs a sequence of operations to clean and process an Excel file named `20230405_2023_MSDC_Tableau_Public_Summary_Data.xlsx`:

1. **Load Data**: Reads data from two sheets of an Excel file.

2. **Prepare Data**: Creates a new composite key, 'School Grade Code', from 'MSDC School Code' and 'Grade' columns in one of the sheets. It also updates the column name 'Matches' to 'Matches_specific_type'.

3. **Merge Data**: Combines data from both Excel sheets based on the columns 'School Grade Code', 'Grade', and 'Lottery Year'.

4. **Data Validation**: Checks to ensure that the sum of 'Matches_specific_type' for each 'School Grade Code' matches with the 'Matches' column.

5. **Data Extraction**: Isolates records where the 'Preference Name' is "No Preference".

6. **Data Classification**: Uses an external list of charter schools to categorize schools in the data as either 'Charter' or 'DCPS' (District of Columbia Public Schools).

7. **Data Transformation**: Transforms the 'MSDC School Code' to a numerical format by extracting numbers and refactors the 'Lottery Year' to a more conventional format. Certain column names are also updated for clarity.

8. **Data Export**: Outputs the processed data as a CSV file named `cleaned_dc_data.csv`.
"""



## Dashboard Usage (`app.py`)

The `app.py` script runs the Shiny dashboard, which provides an interactive way to visualize and filter the DCPS lottery data. Here's a brief overview of the available features:

1. **Select School(s)**: Use the dropdown menu to filter the data based on specific schools. You can select multiple schools at once.
2. **Select Grade(s)**: Use the dropdown menu to filter the data based on specific grades. You can select multiple grades at once.
3. **Lottery Seats, Total Applications, Match - No preference, and Total Waitlisted**: For each of these criteria, you can set minimum and maximum values using the provided input boxes. The dashboard will update the data based on the specified range.
4. **Reset Filters**: Click the "Reset Filters" button to clear all filters and return the dashboard to its initial state.
5. **Download CSV**: Click the "Download CSV" button to download the filtered data as a CSV file.
6. **Bar Charts**: The dashboard includes four bar charts that visualize the number of grades/schools by Total Waitlisted, Lottery Seats, Total Applications, and Match - No preference. These charts update automatically based on the applied filters.
7. **Data Table**: The data table at the bottom of the dashboard displays the filtered data in a tabular format.

## License

This project is licensed under the MIT License.

## Contact

If you want to talk about DCPS data or your organization's data science or dashboarding needs, please contact abigail.haddad@gmail.com
