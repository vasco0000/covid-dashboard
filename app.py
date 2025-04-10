import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback_context
import gc  # Garbage collector

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])

# Custom CSS for dropdown text color
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>COVID-19 Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            /* Fix dropdown text color */
            .Select-value-label, .Select-option {
                color: black !important;
                font-weight: 600 !important;
            }

            /* Fix dropdown background */
            .Select-menu-outer {
                background-color: white !important;
            }

            /* Fix dropdown hover state */
            .Select-option.is-focused {
                background-color: #deebff !important;
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

# Memory-efficient data loading function
def load_data():
    # Only load necessary columns to save memory
    columns_to_load = ['location', 'date', 'total_cases', 'new_cases']

    # Load data with optimized dtypes
    dtype_dict = {
        'location': 'category',
        'total_cases': 'float32',
        'new_cases': 'float32'
    }

    df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv',
                     usecols=columns_to_load,
                     dtype=dtype_dict,
                     parse_dates=['date'])

    # Sort and calculate 7-day average more efficiently
    df = df.sort_values(['location', 'date'])
    df['new_cases'] = df['new_cases'].fillna(0)
    df['total_cases'] = df['total_cases'].fillna(0)

    # Calculate 7-day moving average more efficiently
    df['new_cases_avg'] = df.groupby('location')['new_cases'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )

    return df

# Get unique countries function
def get_countries(df):
    countries = df['location'].unique()
    countries = sorted(countries)
    return countries

# Load data
df = load_data()
countries = get_countries(df)

# Force garbage collection
gc.collect()

# App layout with improved text contrast
app.layout = html.Div(
    style={
        'background': 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
        'minHeight': '100vh',
        'padding': '30px 20px',
        'fontFamily': "'Roboto', sans-serif",
        'color': '#ffffff'  # Brighter text color
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
                        html.Label("Country", style={
                            'marginBottom': '8px',
                            'display': 'block',
                            'color': '#ffffff',  # Brighter label
                            'fontWeight': '600'  # Bolder text
                        }),
                        dcc.Dropdown(
                            id="country-dropdown",
                            options=[{"label": country, "value": country} for country in countries],
                            value="United States",
                            style={
                                'color': 'black',  # Black text for dropdown
                                'fontWeight': '600'  # Bold text
                            }
                        ),
                    ]),

                    # Metric selection
                    html.Div([
                        html.Label("Metric", style={
                            'marginBottom': '8px',
                            'display': 'block',
                            'color': '#ffffff',  # Brighter label
                            'fontWeight': '600'  # Bolder text
                        }),
                        dcc.Dropdown(
                            id="metric-dropdown",
                            options=[
                                {"label": "Total Cases", "value": "total_cases"},
                                {"label": "New Cases", "value": "new_cases"},
                                {"label": "New Cases (7-day Avg)", "value": "new_cases_avg"}
                            ],
                            value="total_cases",
                            style={
                                'color': 'black',  # Black text for dropdown
                                'fontWeight': '600'  # Bold text
                            }
                        ),
                    ]),
                ]),

                # Date range and buttons
                html.Div(style={'marginTop': '20px'}, children=[
                    html.Label("Date Range", style={
                        'marginBottom': '8px',
                        'display': 'block',
                        'color': '#ffffff',  # Brighter label
                        'fontWeight': '600'  # Bolder text
                    }),

                    # Date picker container
                    html.Div(style={
                        'position': 'relative',
                        'marginBottom': '15px'
                    }, children=[
                        dcc.DatePickerRange(
                            id="date-picker",
                            min_date_allowed=df["date"].min(),
                            max_date_allowed=df["date"].max(),
                            initial_visible_month=df["date"].max(),
                            start_date=df["date"].min().strftime('%Y-%m-%d'),
                            end_date=df["date"].max().strftime('%Y-%m-%d'),
                            display_format='YYYY-MM-DD',
                            style={'width': '100%'}
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
                            style={
                                'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                                'border': '1px solid rgba(0, 212, 255, 0.5)',
                                'borderRadius': '8px',
                                'padding': '8px 12px',
                                'cursor': 'pointer',
                                'flex': '1',
                                'minWidth': '120px',
                                'color': 'white',
                                'fontWeight': '600'  # Bolder text
                            }
                        ),
                        html.Button(
                            "Delta",
                            id="delta-wave-btn",
                            style={
                                'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                                'border': '1px solid rgba(0, 212, 255, 0.5)',
                                'borderRadius': '8px',
                                'padding': '8px 12px',
                                'cursor': 'pointer',
                                'flex': '1',
                                'minWidth': '120px',
                                'color': 'white',
                                'fontWeight': '600'  # Bolder text
                            }
                        ),
                        html.Button(
                            "Omicron",
                            id="omicron-wave-btn",
                            style={
                                'backgroundColor': 'rgba(0, 212, 255, 0.2)',
                                'border': '1px solid rgba(0, 212, 255, 0.5)',
                                'borderRadius': '8px',
                                'padding': '8px 12px',
                                'cursor': 'pointer',
                                'flex': '1',
                                'minWidth': '120px',
                                'color': 'white',
                                'fontWeight': '600'  # Bolder text
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
                        html.Label("Show Annotations", style={
                            'marginRight': '10px',
                            'color': '#ffffff',  # Brighter label
                            'fontWeight': '600'  # Bolder text
                        }),
                        dcc.Checklist(
                            id='toggle-annotations',
                            options=[{'label': '', 'value': 'show'}],
                            value=['show'],
                            inline=True,
                            style={'color': 'white'}  # Ensure checkbox text is visible
                        )
                    ]),

                    # Data points toggle
                    html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                        html.Label("Show Data Points", style={
                            'marginRight': '10px',
                            'color': '#ffffff',  # Brighter label
                            'fontWeight': '600'  # Bolder text
                        }),
                        dcc.Checklist(
                            id='toggle-markers',
                            options=[{'label': '', 'value': 'show'}],
                            value=[],
                            inline=True,
                            style={'color': 'white'}  # Ensure checkbox text is visible
                        )
                    ]),

                    # Log scale toggle
                    html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                        html.Label("Use Log Scale", style={
                            'marginRight': '10px',
                            'color': '#ffffff',  # Brighter label
                            'fontWeight': '600'  # Bolder text
                        }),
                        dcc.Checklist(
                            id='toggle-log-scale',
                            options=[{'label': '', 'value': 'log'}],
                            value=[],
                            inline=True,
                            style={'color': 'white'}  # Ensure checkbox text is visible
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
                'position': 'relative'
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
                'fontSize': '14px',  # Slightly larger
                'color': '#ffffff',  # Brighter text
                'marginTop': '20px',
                'fontWeight': '500'  # Semi-bold
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

# Memory-efficient graph callback
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
    try:
        # Basic error handling for missing inputs
        if not country or not metric:
            # Default empty figure
            fig = go.Figure()
            fig.update_layout(
                title="Please select country and metric",
                plot_bgcolor='rgba(22, 33, 62, 0.5)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                font=dict(color='white', size=14)  # Larger, brighter font
            )
            return fig

        # Convert string dates to datetime if they're strings
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)

        # Filter data efficiently
        country_df = df[df["location"] == country].copy()
        filtered_df = country_df[(country_df["date"] >= start_date) & (country_df["date"] <= end_date)]

        # Free memory
        del country_df
        gc.collect()

        # Check if we have data
        if filtered_df.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f"No data available for {country} in selected date range",
                plot_bgcolor='rgba(22, 33, 62, 0.5)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                font=dict(color='white', size=14)  # Larger, brighter font
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

        # Configure the layout - Keep it simple but improve text visibility
        fig.update_layout(
            title=f"{metric.replace('_', ' ').title()} in {country}",
            xaxis_title="Date",
            yaxis_title=metric.replace('_', ' ').title(),
            yaxis_type="log" if use_log_scale and 'log' in use_log_scale else "linear",
            plot_bgcolor='rgba(22, 33, 62, 0.5)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white', size=14),  # Larger, brighter font
            xaxis=dict(
                tickangle=45,
                gridcolor='rgba(255, 255, 255, 0.2)',  # Brighter grid
                tickfont=dict(color='white', size=12)  # Brighter tick labels
            ),
            yaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.2)',  # Brighter grid
                tickformat=".2s",
                tickfont=dict(color='white', size=12)  # Brighter tick labels
            ),
            margin=dict(l=50, r=30, t=50, b=50),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="rgba(22, 33, 62, 0.9)",
                font_size=14,
                font_color="white"
            )
        )

        # Add annotations if enabled - only if we have a reasonable amount of data points
        if show_annotations and 'show' in show_annotations and country == "United States" and len(filtered_df) < 500:
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
                        font=dict(color="white", size=14),  # Brighter, larger font
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
                        font=dict(color="white", size=14),  # Brighter, larger font
                        bgcolor="rgba(255, 153, 0, 0.7)",
                        bordercolor="#ff9900"
                    )

        # Free memory
        del filtered_df
        gc.collect()

        return fig

    except Exception as e:
        # Return error figure
        fig = go.Figure()
        fig.update_layout(
            title=f"Error: {str(e)}",
            plot_bgcolor='rgba(22, 33, 62, 0.5)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white', size=14)  # Larger, brighter font
        )
        return fig

# Add this line for deployment
server = app.server

# Run the app
if __name__ == "__main__":
    app.run_server(debug=False)