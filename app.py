
import pandas as pd
import math
import plotly.graph_objs as go
from shinywidgets import output_widget, register_widget
from shiny import ui, App, render, reactive
from typing import Any
from shiny.ui import div, p



def readCleanCol():
    df = pd.read_csv("2022-2023.csv")
    columns=["School Name", "Grade", "Lottery Seats", "Total Applications", "Total Matches", "Total Waitlisted",
             "Match - No preference"]
    df=df.fillna(0)
    return(df[columns])

# Define a function to create a numeric input box
def numeric_input_box(id: str, label: str, min_val: int, max_val: int, step: int = 1, default_val: int = None):
    return ui.input_numeric(id, label, value=default_val, min=min_val, max=max_val, step=step, width=None)



def defineFigure(df, df_with_bin, raw_column):
    bin_size = 25
    df_with_bin = df.copy()  # Create a new DataFrame
    df_with_bin['Bin'] = df_with_bin[raw_column].apply(lambda x: math.floor(x / bin_size) * bin_size)
    bin_counts = df_with_bin.groupby(['Bin', 'School Name', 'Grade'])[raw_column].count().reset_index(name='Count')
    bin_counts_grouped = bin_counts.groupby(['Bin'])['Count'].sum()

    bars = []
    for bin_value, count in bin_counts_grouped.items():
        schools_with_this_bin = bin_counts[bin_counts['Bin'] == bin_value]
        hover_text = "<br>".join([
           f"School Name: {row['School Name']} <br>Grade: {row['Grade']} <br>{raw_column}: {df.loc[(df['School Name'] == row['School Name']) & (df['Grade'] == row['Grade']), raw_column].values[0]}"
           for _, row in schools_with_this_bin.iterrows()])

        bars.append(go.Bar(
            x=[bin_value],
            y=[count],
            marker_color='blue',
            marker=dict(
               opacity=1.0
            ),
            hovertemplate=hover_text + "<extra></extra>",
            showlegend=False
        ))

    # Create the bar chart
    fig = go.Figure(data=bars)
    # Customize the chart's appearance
    fig.update_layout(
        title={
            'text': f'Number of Grades/Schools by {raw_column}',
            'font': {'family': 'Times New Roman', 'size': 20, 'color': 'black'},
            'x': 0.5,
            'xanchor': 'center',
        },
        xaxis_title=raw_column,
        yaxis_title='Count',
        barmode='stack',
        font=dict(
            family="Times New Roman",
            size=16,
            color="black"
        ),
        plot_bgcolor='#F5F5F5',  # Light gray background for the plot area
        paper_bgcolor='#FFFFFF',  # White background for the entire chart area
        xaxis=dict(
            gridcolor='rgba(200, 200, 200, 0.2)'  # Light gray grid lines
        ),
        yaxis=dict(
            gridcolor='rgba(200, 200, 200, 0.2)'  # Light gray grid lines
        ),
        margin=dict(  # Add some padding around the chart
            l=50,
            r=50,
            b=50,
            t=50,
            pad=4
        )
    )

    # Update the bar colors to a color scheme
    fig.update_traces(
        marker_color='rgba(44, 123, 182, 0.8)',  # Change the bar color
        marker_line_color='rgba(44, 123, 182, 1.0)',  # Add a darker border to the bars
        marker_line_width=1,
        selector=dict(type="bar")
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



app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            body {
              font-family: "Times New Roman", Times, serif;
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
        ui.column(
            11,
            ui.tags.h1("DCPS School Lottery Data for 2023-2024 School Year", class_="title"),
        ),
    ),
    ui.row(
        ui.column(
            6,
            ui.row(
                ui.column(
                    6,
                    ui.input_select("school_filter", "Select School(s)", choices=[], multiple=True)
                ),
                ui.column(
                    6,
                    ui.input_select("grade_filter", "Select Grade(s)", choices=[], multiple=True)
                ),
            ),
        ),
        ui.column(
            6,
            ui.row(
                ui.column(
                    6,
                    numeric_input_box("min_lottery_seats_input", "Min Lottery Seats", min_val=0, max_val=100),
                    numeric_input_box("min_total_applications_input", "Min Total Applications", min_val=0, max_val=100),
                    numeric_input_box("min_no_preference_input", "Min Match - No preference", min_val=0, max_val=100),
                    numeric_input_box("min_total_waitlisted_input", "Min Total Waitlisted", min_val=0, max_val=100),
                ),
                ui.column(
                    6,
                    numeric_input_box("max_lottery_seats_input", "Max Lottery Seats", min_val=0, max_val=100),
                    numeric_input_box("max_total_applications_input", "Max Total Applications", min_val=0, max_val=100),
                    numeric_input_box("max_no_preference_input", "Max Match - No preference", min_val=0, max_val=100),
                    numeric_input_box("max_total_waitlisted_input", "Max Total Waitlisted", min_val=0, max_val=100),
                ),
            ),
        ),
    ),

    ui.input_action_button("reset_filters", "Reset Filters", class_="btn-primary", style="font-size: 0.8rem; padding: 6px 12px; background-color: #1f77b4;"),

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

    ui.output_table("table")
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
    ui.update_select("grade_filter", choices=sorted_grades)
    input.grade_filter.choices = sorted_grades


    # Define function to get min and max values for a specific column in the DataFrame
    def get_min_max(column):
        return int(df[column].min()), int(df[column].max())
      
    
    # Update the choices for the school filter
    ui.update_select("school_filter", choices=df['School Name'].unique().tolist())
    input.school_filter.choices = df['School Name'].unique().tolist()

    # Min and Max Lottery Seats
    min_lottery_seats, max_lottery_seats = get_min_max('Lottery Seats')
    ui.update_numeric("min_lottery_seats_input", value=min_lottery_seats)
    ui.update_numeric("max_lottery_seats_input", value=max_lottery_seats)
    input.min_lottery_seats_input.value = min_lottery_seats
    input.max_lottery_seats_input.value = max_lottery_seats

    # Min and Max Total Applications
    min_total_applications, max_total_applications = get_min_max('Total Applications')
    ui.update_numeric("min_total_applications_input", value=min_total_applications)
    ui.update_numeric("max_total_applications_input", value=max_total_applications)
    input.min_total_applications_input.value = min_total_applications
    input.max_total_applications_input.value = max_total_applications

    # Min and Max Match - No preference
    min_no_preference, max_no_preference = get_min_max("Match - No preference")
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
      min_lottery_seats = input.min_lottery_seats_input()
      max_lottery_seats = input.max_lottery_seats_input()
      min_total_applications = input.min_total_applications_input()
      max_total_applications = input.max_total_applications_input()
      min_no_preference = input.min_no_preference_input()
      max_no_preference = input.max_no_preference_input()
      min_total_waitlisted = input.min_total_waitlisted_input()
      max_total_waitlisted = input.max_total_waitlisted_input()

      filtered_df = df.copy()

      if selected_schools:
        filtered_df = filtered_df[filtered_df['School Name'].isin(selected_schools)]

      if selected_grades:
        filtered_df = filtered_df[filtered_df['Grade'].isin(selected_grades)]

      if min_lottery_seats is not None and max_lottery_seats is not None:
        filtered_df = filtered_df[(filtered_df['Lottery Seats'] >= min_lottery_seats) & (filtered_df['Lottery Seats'] <= max_lottery_seats)]

      if min_total_applications is not None and max_total_applications is not None:
        filtered_df = filtered_df[(filtered_df['Total Applications'] >= min_total_applications) & (filtered_df['Total Applications'] <= max_total_applications)]

      if min_no_preference is not None and max_no_preference is not None:
        filtered_df = filtered_df[(filtered_df["Match - No preference"] >= min_no_preference) & (filtered_df["Match - No preference"] <= max_no_preference)]

      if min_total_waitlisted is not None and max_total_waitlisted is not None:
        filtered_df = filtered_df[(filtered_df['Total Waitlisted'] >= min_total_waitlisted) & (filtered_df['Total Waitlisted'] <= max_total_waitlisted)]

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

        fig_applications = defineFigure(filtered_df, df, 'Total Applications')
        plot_widget_applications = go.FigureWidget(fig_applications)
        register_widget("plot_applications", plot_widget_applications)

        fig_matched = defineFigure(filtered_df, df, "Match - No preference")
        plot_widget_matched = go.FigureWidget(fig_matched)
        register_widget("plot_matched", plot_widget_matched)

    @reactive.Effect()
    def reset_filters():
        if input.reset_filters() is not None:
            ui.update_select("school_filter", selected=[])
            ui.update_select("grade_filter", selected=[])
            ui.update_numeric("min_lottery_seats_input", value=min_lottery_seats)
            ui.update_numeric("max_lottery_seats_input", value=max_lottery_seats)
            ui.update_numeric("min_total_applications_input", value=min_total_applications)
            ui.update_numeric("max_total_applications_input", value=max_total_applications)
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

        path = "2022-2023.csv"
        return path
    
    @output
    @render.table
    def table():
        return filtered_data.get()


app = App(app_ui, server)
