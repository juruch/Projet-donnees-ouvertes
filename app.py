import dash
from dash import dcc, html, Input, Output
from data_loader import extract_all_zips
import os

# Extraire les fichiers ZIP seulement si nécessaire
# Vérifier si un fichier "marker" existe pour éviter de ré-extraire à chaque redémarrage
if not os.path.exists('.extracted'):
    extract_all_zips()
    # Créer un fichier marker pour indiquer que l'extraction est faite
    with open('.extracted', 'w') as f:
        f.write('done')

# Créer l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# IMPORTANT: Cette ligne doit être APRÈS app = dash.Dash()
server = app.server

# Importer les modules des pages après l'instanciation de l'application
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
