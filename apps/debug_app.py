import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import humanize
from datetime import datetime
from dateutil.tz import tzutc

from app import app

from datasources import Datasources
from scheduler import QueryHistory


def debug_table():
    column_names = ["Bucket", "Latest object", "Object modified", "Downloaded", "Checked for update", "Dataframe memory usage"]

    rows = [html.Tr([html.Td(n) for n in column_names])]
    
    for bucket_name, obj in Datasources.query_data.items():
        rows.append(html.Tr([
            html.Td(bucket_name),
            html.Td(obj["filename"]),
            html.Td(humanize.naturaltime(datetime.now(tzutc())-obj["modified"])),
            html.Td(humanize.naturaltime(datetime.now(tzutc())-obj["downloaded"])),
            html.Td(humanize.naturaltime(datetime.now(tzutc())-obj["checked_for_update"])),
            html.Td(humanize.naturalsize(obj["data"].memory_usage(deep=True).sum())),
        ]))

    return html.Table(rows)


def debug_query_history():
    column_names = ["Query name", "Result file",
                    "Execution time", "Status", "Bytes scanned", "Cost", "Execution duration (ms)"]
    
    def format_row(row):
        yield row[0]
        yield row[2]
        yield row[3].strftime("%a %d %b %H:%M:%S")
        yield row[4]
        yield humanize.naturalsize(row[5])
        yield "${:.03f}".format(5*int(row[5])/1e12)
        yield humanize.intcomma(row[6])
    
    rows = [html.Tr([html.Td(n) for n in column_names])]
    
    for event in list(reversed(QueryHistory.history)):
        rows.append(html.Tr(
            [html.Td(x) for x in format_row(event)]
            )
        )
    
    return html.Table(rows)

def debug_dataframes():
    column_names = ["Bucket", "Dataframe memory usage"]
    
    rows = [html.Tr([html.Td(n) for n in column_names])]
    
    for bucket, cache in Datasources.query_data.items():
        rows.append(html.Tr([
            html.Td(bucket),
            html.Td(humanize.naturalsize(cache["data"].memory_usage(deep=True).sum())),
        ]))
    
    return html.Table(rows)

help_panel = [
    html.P("Keep an eye on that cost column."),
]

def generate_layout():
    layout = [
        html.Div([
            html.H4("Current data"),
            debug_table(),
        ], style={"margin-bottom":"50px"}),
        # html.Div([
        #     html.H4("Cached dataframes"),
        #     debug_dataframes(),
        # ], style={"margin-bottom":"50px"}),
        html.Div([
            html.H4("Query history"),
            debug_query_history(),
        ]),
    ]
    return help_panel, layout
