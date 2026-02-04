import dash
from dash import dcc, html, Input, Output

app = dash.Dash(__name__)

# Importer les modules des pages après l'instanciation de l'application
from pages import home
from pages.navigation import create_nav_bar

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Pour gérer la navigation
    create_nav_bar(),  # Appeler la fonction pour créer la barre de navigation
    html.Div(id='page-content')  # Contenu dynamique
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    return home.layout  # Retourner le layout de home.py


# Lancement de l'application
if __name__ == "__main__":
    app.run(debug=True)
