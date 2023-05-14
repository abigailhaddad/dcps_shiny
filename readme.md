# DC School Lottery Data Dashboard

This repository contains two main Python scripts (`cleaning_data.py` and `app.py`) for cleaning data and making a Shiny dashboard application that visualizes the DC lottery data for the 2023-2024 school year.

## Data Cleaning (`cleaning_data.py`)

The `cleaning_data.py` script processes raw data from an Excel file named `20230405_2023_MSDC_Tableau_Public_Summary_Data.xlsx`. The script performs several operations to clean and prepare the data for visualization:

1. **Load and Prepare Data**: Data is loaded from the Excel file and relevant data fields are extracted and prepared for further operations.
2. **Data Merging**: Related data fields are merged to create more comprehensive and usable information.
3. **Data Validation**: Checks are performed to ensure data consistency and integrity.
4. **Data Extraction**: Specific subsets of data are extracted based on defined conditions for focused analysis.
5. **Data Classification**: Schools are classified into 'Charter' and 'DCPS' categories based on information retrieved from an external website.
6. **Data Transformation**: Certain data fields are transformed to more standardized and interpretable formats.
7. **Data Export**: The cleaned and processed data is exported as a CSV file named `cleaned_dc_data.csv`.

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
