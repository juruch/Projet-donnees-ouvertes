import dash
from dash import dcc, html, Input, Output
from data_loader import extract_all_zips

# Extraire les fichiers ZIP une seule fois au démarrage
extract_all_zips()
server=app.server

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
if __name__ == "__main__":import dash
from dash import dcc, html, Input, Output
from data_loader import extract_all_zips

extract_all_zips()

app = dash.Dash(__name__, suppress_callback_exceptions=True)

from pages import home, page1, page2, page3, page4  
from pages.navigation import create_nav_bar

# Layout principal
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Gère l'URL
    create_nav_bar(),                        # Barre de navigation
    html.Div(id='page-content')              # Contenu dynamique
])

# Callback pour changer le contenu en fonction de l'URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/page1':
        return page1.layout
    elif pathname == '/page2':
        return page2.layout
    elif pathname == '/page3':
        return page3.layout
    elif pathname == '/page4':
        return page4.layout
    else:  # Accueil ou URL inconnue
        return home.layout

# Lancement de l'application
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
