import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback_context

# Load and process the data
df = pd.read_csv('owid-covid-data.csv')
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")
df["total_cases"] = df["total_cases"].fillna(0)
df["new_cases"] = df["new_cases"].fillna(0)
# Add 7-day moving average
df["new_cases_avg"] = df.groupby("location")["new_cases"].transform(
    lambda x: x.rolling(window=7, min_periods=1).mean()
)

# Get unique countries
countries = df["location"].unique()
countries.sort()

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])

# App layout with fixed z-index management
app.layout = html.Div(
    style={
        'background': 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
        'minHeight': '100vh',
        'padding': '30px 20px',
        'fontFamily': "'Roboto', sans-serif",
        'color': '#e0e0e0'
    },
    children=[
        # Header
        html.Div([
            html.H1([
                html.I(className="fas fa-virus", style={'marginRight': '15px', 'color': '#ff6b6b'}),
                "COVID-19 Dashboard"
            ], style={
                'color': '#00d4ff',
                'fontSize': '32px',
                'fontWeight': '700',
                'textAlign': 'center',
                'marginBottom': '25px',
                'textShadow': '2px 2px 8px rgba(0, 0, 0, 0.5)',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
            }),
        ]),

        # Main content container
        html.Div(style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '20px'
        }, children=[
            # Data control card
            html.Div(style={
                'backgroundColor': 'rgba(22, 33, 62, 0.9)',
                'borderRadius': '10px',
                'padding': '20px',
                'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.3)',
            }, children=[
                # Country and metric controls
                html.Div(style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                    'gap': '20px'
                }, children=[
                    # Country selection
                    html.Div([
                        html.Label("Country", style={'marginBottom': '8px', 'display': 'block'}),
                        dcc.Dropdown(
                            id="country-dropdown",
                            options=[{"label": country, "value": country} for country in countries],
                            value="United States",
                            style={
                                'backgroundColor': 'rgba(15, 52, 96, 0.9)',
                                'color': 'white'
                            },
                            className='dropdown-high-z'
                        ),
                    ]),

                    # Metric selection
                    html.Div([
                        html.Label("Metric", style={'marginBottom': '8px', 'display': 'block'}),
                        dcc.Dropdown(
                            id="metric-dropdown",
                            options=[
                                {"label": "Total Cases", "value": "total_cases"},
                                {"label": "New Cases", "value": "new_cases"},
                                {"label": "New Cases (7-day Avg)", "value": "new_cases_avg"}
                            ],
                            value="total_cases",
                            style={
                                'backgroundColor': 'rgba(15, 52, 96, 0.9)',
                                'color': 'white'
                            },
                            className='dropdown-high-z'
                        ),
                    ]),
                ]),

                # Date range and buttons
                html.Div(style={'marginTop': '20px'}, children=[
                    html.Label("Date Range", style={'marginBottom': '8px', 'display': 'block'}),

                    # Date picker container
                    html.Div(style={
                        'position': 'relative',
                        'zIndex': '900',
                        'marginBottom': '15px'
                    }, children=[
                        dcc.DatePickerRange(
                            id="date-picker",
                            min_date_allowed=df["date"].min(),
                            max_date_allowed=df["date"].max(),
                            initial_visible_month=df["date"].max(),
                            start_date=df["date"].min().strftime('%Y-%m-%d'),  # Convert to string format
                            end_date=df["date"].max().strftime('%Y-%m-%d'),    # Convert to string format
                            display_format='YYYY-MM-DD',
                            style={'width': '100%'},
                            className='date-picker-high-z'
                        ),
                    ]),

                    # Wave buttons
                    html.Div(style={
                        'display': 'flex',
                        'gap': '10px',
                        'flexWrap': 'wrap',
                        'marginTop': '10px'
                    }, children=[
                        html.Button(
                            "First Wave",
                            id="first-wave-btn",
                            className='wave-btn',
                            style={
                                'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                                'border': '1px solid rgba(0, 212, 255, 0.5)',
                                'borderRadius': '8px',
                                'padding': '8px 12px',
                                'cursor': 'pointer',
                                'flex': '1',
                                'minWidth': '120px',
                                'color': 'white'
                            }
                        ),
                        html.Button(
                            "Delta",
                            id="delta-wave-btn",
                            className='wave-btn',
                            style={
                                'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                                'border': '1px solid rgba(0, 212, 255, 0.5)',
                                'borderRadius': '8px',
                                'padding': '8px 12px',
                                'cursor': 'pointer',
                                'flex': '1',
                                'minWidth': '120px',
                                'color': 'white'
                            }
                        ),
                        html.Button(
                            "Omicron",
                            id="omicron-wave-btn",
                            className='wave-btn',
                            style={
                                'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                                'border': '1px solid rgba(0, 212, 255, 0.5)',
                                'borderRadius': '8px',
                                'padding': '8px 12px',
                                'cursor': 'pointer',
                                'flex': '1',
                                'minWidth': '120px',
                                'color': 'white'
                            }
                        ),
                    ]),
                ]),

                # Display options
                html.Div(style={
                    'marginTop': '20px',
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'gap': '20px'
                }, children=[
                    # Annotations toggle
                    html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                        html.Label("Show Annotations", style={'marginRight': '10px'}),
                        dcc.Checklist(
                            id='toggle-annotations',
                            options=[{'label': '', 'value': 'show'}],
                            value=['show'],
                            inline=True
                        )
                    ]),

                    # Data points toggle
                    html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                        html.Label("Show Data Points", style={'marginRight': '10px'}),
                        dcc.Checklist(
                            id='toggle-markers',
                            options=[{'label': '', 'value': 'show'}],
                            value=[],
                            inline=True
                        )
                    ]),

                    # Log scale toggle
                    html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                        html.Label("Use Log Scale", style={'marginRight': '10px'}),
                        dcc.Checklist(
                            id='toggle-log-scale',
                            options=[{'label': '', 'value': 'log'}],
                            value=[],
                            inline=True
                        )
                    ]),
                ]),
            ]),

            # Graph container
            html.Div(style={
                'backgroundColor': 'rgba(22, 33, 62, 0.9)',
                'borderRadius': '10px',
                'padding': '20px',
                'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.3)',
                'position': 'relative',
                'zIndex': '1'
            }, children=[
                dcc.Loading(
                    id="loading-graph",
                    type="circle",
                    color="#00d4ff",
                    children=[
                        html.Div(id="graph-container", style={'minHeight': '500px'}, children=[
                            dcc.Graph(
                                id="covid-graph",
                                config={
                                    'displayModeBar': True,
                                    'displaylogo': False
                                },
                                style={'height': '500px'}
                            )
                        ])
                    ]
                )
            ]),

            # Footer
            html.Div(style={
                'textAlign': 'center',
                'fontSize': '13px',
                'color': 'rgba(224, 224, 224, 0.7)',
                'marginTop': '20px'
            }, children=[
                html.P([
                    html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                    "Data Source: Our World in Data • Last updated: ",
                    html.Span(df["date"].max().strftime('%Y-%m-%d'))
                ])
            ])
        ]),
    ]
)

# Wave button callback
@app.callback(
    [Output('date-picker', 'start_date'),
     Output('date-picker', 'end_date')],
    [Input('first-wave-btn', 'n_clicks'),
     Input('delta-wave-btn', 'n_clicks'),
     Input('omicron-wave-btn', 'n_clicks')],
    prevent_initial_call=True
)
def update_date_range(first_wave, delta_wave, omicron_wave):
    ctx = callback_context
    if not ctx.triggered:
        return ['2020-01-01', '2024-01-01']

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'first-wave-btn':
        return ['2020-03-01', '2020-06-30']
    elif button_id == 'delta-wave-btn':
        return ['2021-06-01', '2021-11-30']
    elif button_id == 'omicron-wave-btn':
        return ['2021-12-15', '2022-03-31']

    return ['2020-01-01', '2024-01-01']

# Simplified and fixed graph callback
@app.callback(
    Output("covid-graph", "figure"),
    [Input("country-dropdown", "value"),
     Input("metric-dropdown", "value"),
     Input("date-picker", "start_date"),
     Input("date-picker", "end_date"),
     Input("toggle-annotations", "value"),
     Input("toggle-markers", "value"),
     Input("toggle-log-scale", "value")]
)
def update_graph(country, metric, start_date, end_date, show_annotations, show_markers, use_log_scale):
    # Basic error handling for missing inputs
    if not country or not metric:
        # Default empty figure
        fig = go.Figure()
        fig.update_layout(
            title="Please select country and metric",
            plot_bgcolor='rgba(22, 33, 62, 0.5)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white')
        )
        return fig

    # Convert string dates to datetime if they're strings
    try:
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
    except:
        # Use default date range if conversion fails
        start_date = df["date"].min()
        end_date = df["date"].max()

    # Filter data - Simple and robust approach
    filtered_df = df[df["location"] == country].copy()
    filtered_df = filtered_df[(filtered_df["date"] >= start_date) & (filtered_df["date"] <= end_date)]

    # Check if we have data
    if filtered_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No data available for {country} in selected date range",
            plot_bgcolor='rgba(22, 33, 62, 0.5)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white')
        )
        return fig

    # Create the basic figure
    fig = go.Figure()

    # Add the main trace - Keep this simple
    mode = 'lines+markers' if show_markers and 'show' in show_markers else 'lines'
    fig.add_trace(go.Scatter(
        x=filtered_df["date"],
        y=filtered_df[metric],
        mode=mode,
        name=metric.replace('_', ' ').title(),
        line=dict(color='#00d4ff', width=3),
        marker=dict(size=6, color='#00d4ff')
    ))

    # Configure the layout - Keep it simple
    fig.update_layout(
        title=f"{metric.replace('_', ' ').title()} in {country}",
        xaxis_title="Date",
        yaxis_title=metric.replace('_', ' ').title(),
        yaxis_type="log" if use_log_scale and 'log' in use_log_scale else "linear",
        plot_bgcolor='rgba(22, 33, 62, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        xaxis=dict(
            tickangle=45,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickformat=".2s"
        ),
        margin=dict(l=50, r=30, t=50, b=50),
        hovermode="x unified"
    )

    # Add annotations if enabled
    if show_annotations and 'show' in show_annotations and country == "United States":
        # Omicron wave annotation
        omicron_date = pd.Timestamp("2022-01-10")
        if start_date <= omicron_date <= end_date:
            omicron_df = filtered_df[filtered_df["date"] >= omicron_date].head(1)
            if not omicron_df.empty:
                fig.add_annotation(
                    x=omicron_df["date"].iloc[0],
                    y=omicron_df[metric].iloc[0],
                    text="Omicron Wave",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="#ff4d4d",
                    ax=-40,
                    ay=-40,
                    font=dict(color="white"),
                    bgcolor="rgba(255, 77, 77, 0.7)",
                    bordercolor="#ff4d4d"
                )

        # Delta wave annotation
        delta_date = pd.Timestamp("2021-08-15")
        if start_date <= delta_date <= end_date:
            delta_df = filtered_df[filtered_df["date"] >= delta_date].head(1)
            if not delta_df.empty:
                fig.add_annotation(
                    x=delta_df["date"].iloc[0],
                    y=delta_df[metric].iloc[0],
                    text="Delta Wave",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="#ff9900",
                    ax=40,
                    ay=-40,
                    font=dict(color="white"),
                    bgcolor="rgba(255, 153, 0, 0.7)",
                    bordercolor="#ff9900"
                )

    return fig

# CSS for z-index management
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>COVID-19 Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            /* Base styles */
            body {
                margin: 0;
                padding: 0;
                font-family: 'Roboto', sans-serif;
                overflow-x: hidden;
            }

            /* Z-index management */
            .dropdown-high-z .Select-menu-outer {
                z-index: 999 !important;
            }

            .dropdown-high-z .Select-control:focus,
            .dropdown-high-z .is-open .Select-control {
                z-index: 999 !important;
                position: relative;
            }

            .date-picker-high-z {
                z-index: 900 !important;
            }

            #dash-container div[data-dash-is-loading="true"] {
                z-index: 998 !important;
            }

            .DateRangePicker_picker,
            .SingleDatePicker_picker {
                z-index: 999 !important;
            }

            /* Styling fixes */
            .Select-control, .Select-menu-outer {
                background-color: rgba(15, 52, 96, 0.9) !important;
                color: white !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
            }

            .Select-value-label, .Select-option {
                color: white !important;
            }

            .Select-option.is-focused {
                background-color: rgba(0, 212, 255, 0.3) !important;
            }

            /* Date picker styling */
            .DateInput, .DateInput_input {
                background-color: rgba(15, 52, 96, 0.9) !important;
                color: white !important;
                font-size: 14px !important;
            }

            .SingleDatePickerInput, .DateRangePickerInput {
                background-color: transparent !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 4px !important;
            }

            .DayPicker {
                background-color: rgba(22, 33, 62, 0.95) !important;
            }

            .CalendarMonth_caption {
                color: white !important;
            }

            .CalendarDay {
                background-color: rgba(15, 52, 96, 0.8) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                color: white !important;
            }

            .CalendarDay__selected {
                background-color: #00d4ff !important;
                color: #16213e !important;
            }

            /* Button styling */
            .wave-btn:hover {
                background-color: rgba(0, 212, 255, 0.5) !important;
                transform: scale(1.05);
                z-index: 10;
                position: relative;
            }

            /* Loading animation */
            ._dash-loading {
                background-color: rgba(22, 33, 62, 0.7);
                z-index: 999 !important;
            }

            /* Focus elements should be on top */
            *:focus {
                z-index: 999 !important;
                position: relative;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Modify the server for deployment
server = app.server

# Run the app
if __name__ == "__main__":
    app.run(debug=True)