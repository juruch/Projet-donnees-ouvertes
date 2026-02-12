import dash
from dash import dcc, html, Input, Output
import os
import zipfile
import pandas as pd
import pickle


from data_loader import extract_all_zips, load_all_data

extract_all_zips()
data = load_all_data()

foncieres_all = data['foncieres_all']
pop_communes = data['pop_communes']

# Création de l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Importer les modules des pages après l'instanciation de l'application
from pages import home
from pages.navigation import create_nav_bar

# Layout de l'application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Pour gérer la navigation
    create_nav_bar(),  # Appeler la fonction pour créer la barre de navigation
    html.Div(id='page-content')  # Contenu dynamique
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    return home.layout  # Retourner le layout de home.py

# Lancement de l'application
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)