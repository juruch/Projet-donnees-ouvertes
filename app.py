import dash
from dash import dcc, html, Input, Output
import os

# ===== CRÉER L'APP IMMÉDIATEMENT =====
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # CRITIQUE pour Gunicorn

# ===== VARIABLES GLOBALES =====
data = None
data_loaded = False

# ===== IMPORTER LES PAGES =====
try:
    from pages import home, page1, page2, page3, page4
    from pages.navigation import create_nav_bar
    pages_ok = True
except Exception as e:
    print(f"⚠️ Erreur import pages: {e}")
    pages_ok = False

# ===== LAYOUT =====
if pages_ok:
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        create_nav_bar(),
        html.Div(id='page-content'),
        dcc.Interval(id='data-check', interval=2000, n_intervals=0)
    ])
else:
    app.layout = html.Div([html.H1("Erreur de configuration")])

# ===== CHARGER LES DONNÉES APRÈS LE DÉMARRAGE =====
def load_data_once():
    global data, data_loaded
    if not data_loaded:
        try:
            from data_loader import load_all_data
            print("📂 Chargement du cache...")
            data = load_all_data()
            data_loaded = True
            print("✅ Données chargées !")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()

# ===== CALLBACK =====
if pages_ok:
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname'),
         Input('data-check', 'n_intervals')]
    )
    def display_page(pathname, n):
        # Charger les données si pas encore fait
        if not data_loaded:
            load_data_once()
        
        # Si toujours pas chargé, afficher message
        if not data_loaded:
            return html.Div([
                html.H2("⏳ Chargement des données..."),
                html.P("Cela peut prendre 1-2 minutes. Veuillez patienter.")
            ])
        
        # Données OK, afficher la page
        if pathname == '/page1':
            return page1.layout
        elif pathname == '/page2':
            return page2.layout
        elif pathname == '/page3':
            return page3.layout
        elif pathname == '/page4':
            return page4.layout
        else:
            return home.layout

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)

