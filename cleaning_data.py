# -*- coding: utf-8 -*-
"""
Created on Fri May 12 21:56:58 2023

@author: abiga
"""
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re


def get_charter_list():
    # Make a request to the website
    url = 'https://dcpcsb.org/2022-23-public-charter-school-directory'
    r = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find the table on the webpage
    table = soup.find_all('table') 

    # Convert the table to a DataFrame
    df = pd.read_html(str(table))[0]
    charter_list=list(df[0].drop_duplicates())
    first_part_of_name=list(set([i.split(" PCS")[0].split(" - ")[0] for i in charter_list]))
    first_part_of_name=first_part_of_name + ["E.W. Stokes", "DCI"]
    return(first_part_of_name)

def extract_numbers(series):
    return series.apply(lambda x: ''.join(re.findall(r'\d+', str(x))))


def load_data(fileName):
    """
    Load data from Excel file into pandas DataFrames.
    
    Parameters:
    fileName (str): The name of the Excel file.

    Returns:
    grade_level_data, match_type_data: Tuple of DataFrames.
    """
    grade_level_data=pd.read_excel(f"../data/{fileName}", sheet_name="Tableau_Final_Table_forReview")
    match_type_data=pd.read_excel(f"../data/{fileName}", sheet_name="Tableau_Match_Preference_Table")
    return grade_level_data, match_type_data

def prepare_data(match_type_data):
    """
    Prepare data for merging by creating new columns and renaming existing ones.
    
    Parameters:
    match_type_data (DataFrame): The DataFrame to be prepared.

    Returns:
    match_type_data: The prepared DataFrame.
    """
    # create new column 'School Grade Code' in df2 as concatenation of 'MSDC School Code' and 'Grade'
    match_type_data['School Grade Code'] = match_type_data['MSDC School Code'].astype(str) + ' ' + match_type_data['Grade'].astype(str) 
    match_type_data=match_type_data.rename(columns={'Matches': 'Matches_specific_type'})
    return match_type_data

def merge_data(grade_level_data, match_type_data):
    """
    Merge two DataFrames on specified columns.
    
    Parameters:
    grade_level_data, match_type_data (DataFrame): The DataFrames to be merged.

    Returns:
    merged_df: The merged DataFrame.
    """
    # merge the dataframes
    merged_df = pd.merge(grade_level_data, match_type_data, how='outer', on=['School Grade Code', 'Grade', 'Lottery Year'], 
                     indicator=True)
    merged_df=merged_df.rename(columns={'School Name_x': 'School Name'}).drop(columns=["School Name_y", "_merge"])
    return merged_df

def check_sums(grade_level_data, match_type_data):
    """
    Check if the sum of 'Matches_specific_type' equals 'Matches' for each 'School Grade Code'.
    
    Parameters:
    grade_level_data, match_type_data (DataFrame): The DataFrames to be checked.

    Returns:
    sums_both: DataFrame showing the sums for each 'School Grade Code' and whether they are equal.
    """
    sums_to_check= match_type_data.groupby('School Grade Code').sum()['Matches_specific_type'].reset_index()
    sums_both=grade_level_data.merge(sums_to_check, left_on=['School Grade Code'], right_on=['School Grade Code'])
    return sums_both.loc[sums_both['Matches']!=sums_both['Matches_specific_type']]

def main():
    """
    Main function to load data, prepare it, merge it, and check sums.
    """
    fileName = "20230405_2023_MSDC_Tableau_Public_Summary_Data.xlsx"
    grade_level_data, match_type_data = load_data(fileName)
    match_type_data = prepare_data(match_type_data)
    merged_df = merge_data(grade_level_data, match_type_data)
    unequal_sums = check_sums(grade_level_data, match_type_data)
    print(unequal_sums)
    return(merged_df)

if __name__ == "__main__":
    merged_df=main()
    no_preference=merged_df.loc[merged_df['Preference Name']=="No Preference"]
    print([i for i in merged_df['School Grade Code'].unique() if i not in no_preference['School Grade Code'].unique()])
    keepCols=['MSDC School Code', 'School Name', 'Grade', 'Lottery Year', 'Seats', 'Matches', 'Waitlist Length', 'Matches_specific_type']
    no_preference=no_preference[keepCols]
    no_preference['MSDC School Code']=extract_numbers(no_preference['MSDC School Code']).astype(float)

    charter_list = get_charter_list()
    no_preference['DCPS'] = no_preference['School Name'].apply(
        lambda x: 'Charter' if any(c.lower() in x.lower() for c in charter_list) or 'pcs' in x.lower() or 'charter' in x.lower() else 'DCPS')


    no_preference['Year']=no_preference['Lottery Year'].str.replace('SY', '20').str.replace('-', '-20')
    no_preference=no_preference.rename(columns={'Matches_specific_type':'Match - No Preference', 
                                 'Seats':  'Lottery Seats', 'Matches': 'Matches on Results Day',
                                 'Waitlist Length': 'Total Waitlisted'})
    no_preference.to_csv("cleaned_dc_data.csv")
    
    
    

