# -*- coding: utf-8 -*-
"""
Created on Fri May  5 15:36:59 2023

@author: abiga
"""

import requests
import pandas as pd
import io


def get_dict_links():
    return {
        "https://enrolldcps.dc.gov/sites/dcpsenrollment/files/page_content/attachments/20230331.DCPS_.SY23-24.Lottery.Results_1.xlsx": "SY23-24 Lottery Summary Results",
        "https://enrolldcps.dc.gov/sites/dcpsenrollment/files/page_content/attachments/20221003.DCPS_.SY22.23.Lottery.Results.xlsx": "SY22-23 Lottery Summary Results",
        "https://enrolldcps.dc.gov/sites/dcpsenrollment/files/page_content/attachments/20210401.DCPS_.SY21.22.Lottery.Results.xlsx": "Long.Lottery.Results.2021",
        "https://dcps.dc.gov/sites/default/files/dc/sites/dcps/publication/attachments/20200327.DCPS_.SY20.21.Lottery.Results_0.xlsx": "Long.Lottery.Results.2020"
    }

def get_column_mapping():
    return({
    "DCPS School Code": ["DCPS.School.Code"],
    "MSDC School Code": ["MSDC.School.Code"],
    "School Name": ["School.Name"],
    "School Ward": [],
    "School Type": [],
    "Program": ["School.Program"],
    "Grade": ["Grade"],
    "Lottery Seats": ["Total.Seats.by.Grade"],
    "Total Applications": ["Total.Applications.by.Grade"],
    "Total Matches": ["Matches"],
    "Total Waitlisted": ["Waitlisted"],
    # Other columns not mentioned in the older files are not included here
})

def get_school_name_mapping():
    return({
    "Phelps Architecture, Construction and Engineering High School": [
        "Phelps Architecture Construction and Engineering High School"
    ],
    "Duke Ellington School of the Arts - Dance program": [
        "Duke Ellington School of the Arts - Dance"
    ],
    "Duke Ellington School of the Arts - Instrumental Music program": [
        "Duke Ellington School of the Arts - Instrumental Music"
    ],
    "Duke Ellington School of the Arts - Literary Media and Communications program": [
        "Duke Ellington School of the Arts - Literary Media and Communications"
    ],
    "Duke Ellington School of the Arts - Museum Studies program": [
        "Duke Ellington School of the Arts - Museum Studies"
    ],
    "Duke Ellington School of the Arts - Technical Design and Production program": [
        "Duke Ellington School of the Arts - Technical Design and Production"
    ],
    "Duke Ellington School of the Arts - Theater program": [
        "Duke Ellington School of the Arts - Theatre"
    ],
    "Duke Ellington School of the Arts - Visual Arts program": [
        "Duke Ellington School of the Arts - Visual Arts"
    ],
    "Duke Ellington School of the Arts - Vocal Music program": [
        "Duke Ellington School of the Arts - Vocal Music"
    ]})

def download_and_read_excel_files(dict_links):
    dfs = {}

    for url, sheet_name in dict_links.items():
        response = requests.get(url)
        if response.status_code == 200:
            # Read the Excel file from the response content
            excel_file = io.BytesIO(response.content)
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # Add the DataFrame to the dictionary with the filename as the key
            filename = url.split("/")[-1]
            dfs[filename] = df
        else:
            print(f"Error downloading file from {url}")

    return dfs



def standardize_and_concatenate_dataframes(filename_df_pairs, column_mapping):
    standardized_dataframes = []

    for filename, df in filename_df_pairs.items():
        standardized_columns = {}
        for new_column, old_columns in column_mapping.items():
            for old_column in old_columns:
                if old_column in df.columns:
                    standardized_columns[old_column] = new_column

        # Rename columns in the DataFrame
        df = df.rename(columns=standardized_columns)

        # Filter the DataFrame to keep only the columns specified in column_mapping
        df = df[[new_column for new_column in column_mapping.keys() if new_column in df.columns]]
        
        df['Source']=filename
        standardized_dataframes.append(df)

    # Concatenate the standardized DataFrames
    concatenated_df = pd.concat(standardized_dataframes, ignore_index=True)
    concatenated_df['Grade']=concatenated_df['Grade'].astype(str)
    return concatenated_df


def print_diagnostics(combined_df):
    print("Diagnostics:")
    print("------------")
    for column in combined_df.columns:
        if column == "Source":
            continue

        print(f"Column: {column}")
        print("Non-missing values percentage per dataset:")

        for filename in combined_df["Source"].unique():
            df = combined_df[combined_df["Source"] == filename]
            non_missing_count = df[column].notna().sum()
            total_rows = len(df)
            percentage = (non_missing_count / total_rows) * 100
            print(f"  {filename}: {percentage:.2f}%")

        print("Overlap in values across datasets:")
        values_sets = [
            set(combined_df[combined_df["Source"] == filename][column].dropna()) for filename in combined_df["Source"].unique()
        ]

        if len(values_sets) > 1:
            intersection = set.intersection(*values_sets)
            print(f"  {len(intersection)} overlapping values\n")
        else:
            print("  Not applicable (only one dataset has this column)\n")

def rename_schools(df, school_name_mapping):
    for standardized_name, variations in school_name_mapping.items():
        for variation in variations:
            df.loc[df["School Name"] == variation, "School Name"] = standardized_name
    return df


def convert_columns_to_numbers(df: pd.DataFrame) -> pd.DataFrame:
    return df.convert_dtypes()

def main():
    # Download the Excel files and read the specified sheets into DataFrames
    dict_links = get_dict_links()
    filename_df_pairs = download_and_read_excel_files(dict_links)
    
    # Standardize and concatenate the DataFrames
    column_mapping = get_column_mapping()
    combined_df = standardize_and_concatenate_dataframes(filename_df_pairs, column_mapping)
    
    # Rename schools and convert columns to numbers
    school_name_mapping = get_school_name_mapping()
    combined_df = rename_schools(combined_df, school_name_mapping)
    combined_df = convert_columns_to_numbers(combined_df)
    
    # Example usage: print the first 5 rows of the combined DataFrame
    print(combined_df.head())
    
    # Run the diagnostics on the combined DataFrame
    print_diagnostics(combined_df)
    return(combined_df)


if __name__ == "__main__":
    combined_df=main()
    cols_to_keep=['School Name','Grade', 'Lottery Seats', 'Total Applications',
    'Total Matches', 'Total Waitlisted']
    combined_df







