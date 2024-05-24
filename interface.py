import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pymysql

# Charger les données de la base de données
db = pymysql.connect(host='localhost',
                     user='root',
                     password='',
                     database='weather_dataWarehouse',
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)

cursor = db.cursor()
cursor.execute("SELECT * FROM Weather_Fact INNER JOIN Station_Dim ON Weather_Fact.StationID = Station_Dim.StationID INNER JOIN Date_Dim ON Weather_Fact.Date_ID = Date_Dim.Date_ID")
rows = cursor.fetchall()
df = pd.DataFrame(rows)

# Dictionnaire pour mapper les mesures climatiques à des descriptions textuelles
measure_descriptions = {
    'PRCP': 'Précipitations (en millimètres)',
    'TAVG': 'Température moyenne (en degrés Celsius)',
    'TMAX': 'Température maximale (en degrés Celsius)',
    'TMIN': 'Température minimale (en degrés Celsius)',
    'SNWD': 'Profondeur de la neige (en millimètres)',
    'PGTM': 'Pression atmosphérique (en hectopascals)',
    'SNOW': 'Chute de neige (en millimètres)',
    'WDFG': 'Direction du vent (en degrés)',
    'WSFG': 'Vitesse maximale du vent (en km/h)'
}

# Créer l'application Dash
app = dash.Dash(__name__)

# Définir la mise en page de l'application
app.layout = html.Div(
    style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f4f4f4', 'padding': '20px'},
    children=[
        html.H1(
            children='Tableau de bord des données météorologiques',
            style={'textAlign': 'center', 'color': '#333', 'marginBottom': '40px'}
        ),
        html.Div(
            style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px', 'justifyContent': 'space-between', 'marginBottom': '20px'},
            children=[
                dcc.Dropdown(
                    id='station-dropdown',
                    options=[{'label': i, 'value': i} for i in df['Name'].unique()],
                    value=df['Name'].iloc[0],
                    style={'width': '48%', 'padding': '10px', 'fontSize': '16px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
                ),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': i, 'value': i} for i in df['Year'].unique()],
                    value=df['Year'].min(),
                    style={'width': '48%', 'padding': '10px', 'fontSize': '16px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
                ),
                dcc.Dropdown(
                    id='season-dropdown',
                    options=[{'label': i, 'value': i} for i in ['Spring', 'Summer', 'Autumn', 'Winter']],
                    value='Winter',
                    style={'width': '48%', 'padding': '10px', 'fontSize': '16px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
                ),
                dcc.Dropdown(
                    id='quarter-dropdown',
                    options=[{'label': 'Q' + str(i), 'value': i} for i in range(1, 5)],
                    value=1,
                    style={'width': '48%', 'padding': '10px', 'fontSize': '16px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
                ),
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[{'label': i, 'value': i} for i in df['Month'].unique()],
                    value=df['Month'].min(),
                    style={'width': '48%', 'padding': '10px', 'fontSize': '16px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
                ),
                dcc.Dropdown(
                    id='measure-dropdown',
                    options=[{'label': v, 'value': k} for k, v in measure_descriptions.items()],
                    value='TMAX',
                    style={'width': '48%', 'padding': '10px', 'fontSize': '16px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
                )
            ]
        ),
        html.Div(
            style={'width': '100%', 'border': '1px solid #ccc', 'borderRadius': '5px', 'padding': '10px', 'backgroundColor': '#fff', 'marginBottom': '20px'},
            children=[
                dcc.Graph(id='weather-graph')
            ]
        ),
        html.Div(
            style={'width': '100%', 'border': '1px solid #ccc', 'borderRadius': '5px', 'padding': '10px', 'backgroundColor': '#fff', 'marginBottom': '20px'},
            children=[
                dcc.Graph(id='weather-map')
            ]
        ),
        html.Div(
            style={'width': '100%', 'border': '1px solid #ccc', 'borderRadius': '5px', 'padding': '10px', 'backgroundColor': '#fff', 'marginBottom': '20px'},
            children=[
                dcc.Graph(id='weather-histogram')
            ]
        )
    ]
)

# Définir les callbacks pour mettre à jour les graphiques en fonction des filtres
@app.callback(
    Output('weather-graph', 'figure'),
    [Input('station-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('season-dropdown', 'value'),
     Input('quarter-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('measure-dropdown', 'value')]
)
def update_weather_graph(selected_station, selected_year, selected_season, selected_quarter, selected_month, selected_measure):
    # Map season to a set of months
    season_months = {
        'Spring': [3, 4, 5],
        'Summer': [6, 7, 8],
        'Autumn': [9, 10, 11],
        'Winter': [12, 1, 2]
    }

    # Map quarter to a set of months
    quarter_months = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    filtered_df = df[(df['Name'] == selected_station) & (df['Year'] == selected_year) & (df['Month'].isin(season_months[selected_season])) & (df['Month'].isin(quarter_months[selected_quarter])) & (df['Month'] == selected_month)]
    fig = px.line(filtered_df, x='Day', y=selected_measure, title=f'{measure_descriptions[selected_measure]} over Days')
    fig.update_traces(line=dict(color='blue'))
    fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
    return fig

@app.callback(
    Output('weather-map', 'figure'),
    [Input('station-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('season-dropdown', 'value'),
     Input('quarter-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('measure-dropdown', 'value')]
)
def update_weather_map(selected_station, selected_year, selected_season, selected_quarter, selected_month, selected_measure):
    # Map season to a set of months
    season_months = {
        'Spring': [3, 4, 5],
        'Summer': [6, 7, 8],
        'Autumn': [9, 10, 11],
        'Winter': [12, 1, 2]
    }

    # Map quarter to a set of months
    quarter_months = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    filtered_df = df[(df['Name'] == selected_station) & (df['Year'] == selected_year) & (df['Month'].isin(season_months[selected_season])) & (df['Month'].isin(quarter_months[selected_quarter])) & (df['Month'] == selected_month)]

    fig = go.Figure(data=go.Scattergeo(
        lon=filtered_df['Longitude'],
        lat=filtered_df['Latitude'],
        text=filtered_df[selected_measure],
        mode='markers',
        marker_color=filtered_df[selected_measure],
        marker=dict(colorscale='Viridis', showscale=True)
    ))

    fig.update_layout(
        title_text='Weather Measure by Location',
        geo_scope='world',
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    return fig

@app.callback(
    Output('weather-histogram', 'figure'),
    [Input('station-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('season-dropdown', 'value'),
     Input('quarter-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('measure-dropdown', 'value')]
)
def update_weather_histogram(selected_station, selected_year, selected_season, selected_quarter, selected_month, selected_measure):
    # Map season to a set of months
    season_months = {
        'Spring': [3, 4, 5],
        'Summer': [6, 7, 8],
        'Autumn': [9, 10, 11],
        'Winter': [12, 1, 2]
    }

    # Map quarter to a set of months
    quarter_months = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    filtered_df = df[(df['Name'] == selected_station) & (df['Year'] == selected_year) & (df['Month'].isin(season_months[selected_season])) & (df['Month'].isin(quarter_months[selected_quarter])) & (df['Month'] == selected_month)]
    fig = px.histogram(filtered_df, x=selected_measure, title=f'Distribution of {measure_descriptions[selected_measure]}')
    fig.update_traces(marker_color='blue')
    fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)



