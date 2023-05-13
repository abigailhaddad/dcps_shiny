
import pandas as pd
import math
import plotly.graph_objs as go
from shinywidgets import output_widget, register_widget
from shiny import ui, App, render, reactive
from typing import Any
from shiny.ui import div


import os
os.chdir(r"C:\Users\abiga\OneDrive\Documents\PythonScripts\shiny\my_app")
def readCleanCol():
    df = pd.read_csv("cleaned_dc_data.csv")
    columns=["School Name", "Grade", "Lottery Seats", "Matches on Results Day", "Total Waitlisted",
             "Match - No Preference", "Year", "DCPS"]
    df=df.fillna(0)
    return(df[columns])

# Define a function to create a numeric input box
def numeric_input_box(id: str, label: str, min_val: int, max_val: int, step: int = 1, default_val: int = None, width=None):
    return ui.input_numeric(id, label, value=default_val, min=min_val, max=max_val, step=step, width=width)


def defineFigure(df, df_with_bin, raw_column):
    bin_size = 25
    df_with_bin = df.copy()  # Create a new DataFrame
    df_with_bin['Bin'] = df_with_bin[raw_column].apply(lambda x: math.floor(x / bin_size) * bin_size)
    bin_counts = df_with_bin.groupby(['Year', 'Bin', 'School Name', 'Grade'])[raw_column].count().reset_index(name='Count')
    years = sorted(df['Year'].unique())
    colors = ['rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)']  # Add more colors if needed
    bars = []
    for year, color in zip(years, colors[:len(years)]):
        year_bin_counts = bin_counts[bin_counts['Year'] == year]
        bin_counts_grouped = year_bin_counts.groupby(['Bin'])['Count'].sum()

        first_bin_for_year = True
        for bin_value, count in bin_counts_grouped.items():
            schools_with_this_bin = year_bin_counts[year_bin_counts['Bin'] == bin_value]
            hover_text = "<br>".join([
               f"<br>School Name: {row['School Name']} <br>Grade: {row['Grade']} <br>Year: {row['Year']} <br>{raw_column}: {df.loc[(df['School Name'] == row['School Name']) & (df['Grade'] == row['Grade']), raw_column].values[0]}"
               for _, row in schools_with_this_bin.iterrows()])

            bars.append(go.Bar(
                x=[bin_value],
                y=[count],
                marker_color=color,
                marker=dict(
                   opacity=1.0
                ),
                hovertemplate=hover_text + "<extra></extra>",
                name=str(year),
                showlegend=first_bin_for_year
            ))
            first_bin_for_year = False
    # Create the bar chart
    fig = go.Figure(data=bars)
    # Customize the chart's appearance
    fig.update_layout(height=350,
        title={
            'text': f'Number of Grades/Schools by {raw_column}',
            'font': {'family': 'Arial', 'size': 20, 'color': 'black'},
            'x': 0.5,
            'xanchor': 'center',
        },
        xaxis_title=raw_column,
        yaxis_title='Count',
        barmode='stack',
        font=dict(
            family="Arial",
            size=16,
            color="black"
        ),
        plot_bgcolor='#F5F5F5',  # Light gray background for the plot area
        paper_bgcolor='#FFFFFF',  # White background for the entire chart area
        xaxis=dict(
            gridcolor='rgba(200, 200, 200, 0.2)'  # Light gray grid lines
        ),
        yaxis=dict(
            gridcolor='rgba(200, 200, 200, 0.2)',  # Light gray grid lines,
        ),
        margin=dict(  # Add some padding around the chart
            l=50,
            r=50,
            b=50,
            t=50,
            pad=4
        ),
        legend=dict(
            title="School Year",
            font=dict(
                size=12
            ),
            x=.95,
            y=.95,
            xanchor='right',
            yanchor='top',
            bordercolor='rgba(0, 0, 0, .5)',  # Black border color
            borderwidth=1
        )
    )

    fig.update_layout(bargap=0,
                      bargroupgap=0,
                      )

    return fig




def get_min_max_lottery_seats(df):
    min_lottery_seats = df['Lottery Seats'].min()
    max_lottery_seats = df['Lottery Seats'].max()
    return min_lottery_seats, max_lottery_seats

def make_download_button(id: str, label: str, extra: Any = None):
    return ui.row(
        div(
            div(
                {"class": "card-body", "style": "padding-top: 20px;"},
                extra,
                ui.download_button(id, label, class_="btn-primary", style="font-size: 0.8rem; padding: 6px 12px; background-color: #1f77b4;"),
            ),
        ),
    )
    
def make_reset_button(id: str, label: str, extra: Any = None):
    return ui.row(
        div(
            div(
                {"class": "card-body", "style": "padding-top: 20px;"},
                extra,
                ui.input_action_button(id, label, class_="btn-primary", style="font-size: 0.8rem; padding: 6px 12px; background-color: #1f77b4;"),
            ),
        ),
    )



app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            body {
              font-family: "Arial", sans-serif;
              color: black;
              padding-left: 20px;
              padding-right: 20px;
            }
            .title {
              font-size: 30px;
              text-align: center;
              font-weight: bold;
              margin-bottom: 20px;
              margin-top: 20px;
            }
            .column-text {
              text-align: left;
              margin-bottom: 20px;
            }
            .table th {
    text-align: left;
    padding-left: 10px;
}
        """)
    ),
    ui.row(
        ui.column(
            1,
            make_download_button(
                "download1",
                label="Download CSV",
            ),
        ),
        ui.column(1,
        make_reset_button("reset_filters", "Reset Filters"),
        ),
        ui.column(
            10,
            ui.tags.h1("DC School Lottery Data for 2023-2024 School Year", class_="title"),
        ),
    ),
    ui.row(
        ui.column(
            12,
            ui.row(
                ui.column(
                    3,
                    ui.input_selectize("school_filter", "Select School(s)", choices=[], multiple=True)
                ),
                ui.column(
                    3,
                    ui.input_selectize("year_filter", "Select Year(s)", choices=[], multiple=True)
                ),
                ui.column(
                    3,
                    ui.input_selectize("grade_filter", "Select Grade(s)", choices=[], multiple=True)
                ),
                ui.column(
                    3,
                    ui.input_selectize("type_filter", "Select DCPS/Charter", choices=[], multiple=True)
                ),
            ),
        ),
    ),
    ui.row(
        ui.column(
            3,
            ui.row(
                ui.HTML("<h5>Lottery Seats</h5>"),
                numeric_input_box("min_lottery_seats_input", "Min", min_val=0, max_val=100, width="40%"),
                numeric_input_box("max_lottery_seats_input", "Max", min_val=0, max_val=100, width="40%")
            ),
        ),
        ui.column(
            3,
            ui.row(
                ui.HTML("<h5>Matches on Results Day</h5>"),
                numeric_input_box("min_total_matches_input", "Min", min_val=0, max_val=100, width="40%"),
                numeric_input_box("max_total_matches_input", "Max", min_val=0, max_val=100, width="40%"),
            ),
        ),
        ui.column(
          3,
          ui.row(
                ui.HTML("<h5>Match - No Preference</h5>"),
                numeric_input_box("min_no_preference_input", "Min", min_val=0, max_val=100, width="40%"),
                numeric_input_box("max_no_preference_input", "Max", min_val=0, max_val=100, width="40%")
          ),
        ),
        ui.column(
          3,
          ui.row(
                ui.HTML("<h5>Total Waitlisted</h5>"),
                numeric_input_box("min_total_waitlisted_input", "Min", min_val=0, max_val=100, width="40%"),
                numeric_input_box("max_total_waitlisted_input", "Max", min_val=0, max_val=100, width="40%")
                      
          )
        ),
    ),


    ui.row(
        ui.column(
            6,
            output_widget("plot_waitlist")
        ),
        ui.column(
            6,
            output_widget("plot_lottery"),
        )),
    ui.row(
        ui.column(
            6,
            output_widget("plot_applications")
        ),
        ui.column(
            6,
            output_widget("plot_matched"),
        )),

    ui.output_table("table"),
    ui.row(
        ui.column(
            12,
            ui.tags.a("View code and readme on GitHub", href="https://github.com/abigailhaddad/dcps_shiny", target="_blank")
        )
    ),
)




def server(input, output, session):
    df = readCleanCol()
    filtered_data = reactive.Value(df)


    # Define a custom sorting function for the grade filter
    def custom_grade_sort(grade):
        order = {'PK3': -2, 'PK4': -1, 'K': 0}
        return order[grade] if grade in order else int(grade)

    # Sort the list of unique grade choices and update the grade filter
    sorted_grades = sorted(df['Grade'].unique().tolist(), key=custom_grade_sort)
    ui.update_select("grade_filter", choices=sorted_grades, selected=sorted_grades)
    input.grade_filter.choices = sorted_grades
  

    # Define function to get min and max values for a specific column in the DataFrame
    def get_min_max(column):
        return int(df[column].min()), int(df[column].max())
      
    
    # Update the choices for the school filter
    school_choices = df['School Name'].unique().tolist()
    ui.update_select("school_filter", choices=school_choices, selected=school_choices)
    input.school_filter.choices = school_choices
    
    # Update the choices for the year filter
    year_choices = df['Year'].unique().tolist()
    ui.update_select("year_filter", choices=year_choices, selected="2023-2024")
    input.year_filter.choices = year_choices
    
    # Update the choices for the type filter
    type_choices = df['DCPS'].unique().tolist()
    ui.update_select("type_filter", choices=type_choices, selected=type_choices)
    input.type_filter.choices = type_choices

    # Min and Max Lottery Seats
    min_lottery_seats, max_lottery_seats = get_min_max('Lottery Seats')
    ui.update_numeric("min_lottery_seats_input", value=min_lottery_seats)
    ui.update_numeric("max_lottery_seats_input", value=max_lottery_seats)
    input.min_lottery_seats_input.value = min_lottery_seats
    input.max_lottery_seats_input.value = max_lottery_seats

    # Min and Max Matches on Results Day
    min_total_matches, max_total_matches = get_min_max('Matches on Results Day')
    ui.update_numeric("min_total_matches_input", value=min_total_matches)
    ui.update_numeric("max_total_matches_input", value=max_total_matches)
    input.min_total_matches_input.value = min_total_matches
    input.max_total_matches_input.value = max_total_matches

    # Min and Max Match - No preference
    min_no_preference, max_no_preference = get_min_max("Match - No Preference")
    ui.update_numeric("min_no_preference_input", value=min_no_preference)
    ui.update_numeric("max_no_preference_input", value=max_no_preference)
    input.min_no_preference_input.value = min_no_preference
    input.max_no_preference_input.value = max_no_preference

    # Min and Max Total Waitlisted
    min_total_waitlisted, max_total_waitlisted = get_min_max('Total Waitlisted')
    ui.update_numeric("min_total_waitlisted_input", value=min_total_waitlisted)
    ui.update_numeric("max_total_waitlisted_input", value=max_total_waitlisted)
    input.min_total_waitlisted_input.value = min_total_waitlisted
    input.max_total_waitlisted_input.value = max_total_waitlisted



    @reactive.Effect
    def update_filtered_data():
        selected_schools = input.school_filter()
        selected_grades = input.grade_filter()
        selected_years = input.year_filter()
        selected_types = input.type_filter()

        min_lottery_seats_value = input.min_lottery_seats_input()
        max_lottery_seats_value = input.max_lottery_seats_input()
        min_total_matches_value = input.min_total_matches_input()
        max_total_matches_value = input.max_total_matches_input()
        min_no_preference_value = input.min_no_preference_input()
        max_no_preference_value = input.max_no_preference_input()
        min_total_waitlisted_value = input.min_total_waitlisted_input()
        max_total_waitlisted_value = input.max_total_waitlisted_input()

        filtered_df = df.copy()

        if selected_schools:
            filtered_df = filtered_df[filtered_df['School Name'].isin(selected_schools)]
            
        if selected_years:
            filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)]

        if selected_grades:
            filtered_df = filtered_df[filtered_df['Grade'].isin(selected_grades)]
            
        if selected_types:
            filtered_df = filtered_df[filtered_df['DCPS'].isin(selected_types)]

        filtered_df = filtered_df[(filtered_df['Lottery Seats'] >= min_lottery_seats_value) & (filtered_df['Lottery Seats'] <= max_lottery_seats_value)]

        filtered_df = filtered_df[(filtered_df['Matches on Results Day'] >= min_total_matches_value) & (filtered_df['Matches on Results Day'] <= max_total_matches_value)]

        filtered_df = filtered_df[(filtered_df["Match - No Preference"] >= min_no_preference_value) & (filtered_df["Match - No Preference"] <= max_no_preference_value)]

        filtered_df = filtered_df[(filtered_df['Total Waitlisted'] >= min_total_waitlisted_value) & (filtered_df['Total Waitlisted'] <= max_total_waitlisted_value)]

        filtered_data.set(filtered_df)


    @reactive.Effect
    def update_figures():

        filtered_df = filtered_data.get()
        fig_waitlist = defineFigure(filtered_df, df, 'Total Waitlisted')
        plot_widget_waitlist = go.FigureWidget(fig_waitlist)
        register_widget("plot_waitlist", plot_widget_waitlist)

        fig_lottery = defineFigure(filtered_df, df, 'Lottery Seats')
        plot_widget_lottery = go.FigureWidget(fig_lottery)
        register_widget("plot_lottery", plot_widget_lottery)

        fig_applications = defineFigure(filtered_df, df, 'Matches on Results Day')
        plot_widget_applications = go.FigureWidget(fig_applications)
        register_widget("plot_applications", plot_widget_applications)

        fig_matched = defineFigure(filtered_df, df, "Match - No Preference")
        plot_widget_matched = go.FigureWidget(fig_matched)
        register_widget("plot_matched", plot_widget_matched)

    @reactive.Effect()
    def reset_filters():
        if input.reset_filters() is not None:
            ui.update_select("school_filter", selected=[])
            ui.update_select("grade_filter", selected=[])
            ui.update_select("year_filter", selected=["2023-2024"])
            ui.update_select("type_filter", selected=["DCPS", "Charter"])
            ui.update_numeric("min_lottery_seats_input", value=min_lottery_seats)
            ui.update_numeric("max_lottery_seats_input", value=max_lottery_seats)
            ui.update_numeric("min_total_matches_input", value=min_total_matches)
            ui.update_numeric("max_total_matches_input", value=max_total_matches)
            ui.update_numeric("min_no_preference_input", value=min_no_preference)
            ui.update_numeric("max_no_preference_input", value=max_no_preference)
            ui.update_numeric("min_total_waitlisted_input", value=min_total_waitlisted)
            ui.update_numeric("max_total_waitlisted_input", value=max_total_waitlisted)

            
    @session.download()
    def download1():
        """
        This is the simplest case. The implementation simply returns the name of a file.
        Note that the function name (`download1`) determines which download_button()
        corresponds to this function.
        """

        return path
    
    @output
    @render.table
    def table():
        return filtered_data.get()


app = App(app_ui, server)
