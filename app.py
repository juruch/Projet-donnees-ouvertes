import os
import threading

import dash
from dash import dcc, html, Input, Output

# =============================
# APP + SERVER (Gunicorn)
# =============================
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # important pour: gunicorn app:server

# Healthcheck: Render a besoin d'une route qui répond tout de suite
@server.route("/healthz")
def healthz():
    return "ok", 200

# =============================
# ETAT GLOBAL (cache en mémoire)
# =============================
data = None
data_loaded = False
data_error = None
_data_lock = threading.Lock()

# =============================
# IMPORT DES PAGES (sans crash)
# =============================
pages_ok = True
try:
    from pages import home, page1, page2, page3, page4
    from pages.navigation import create_nav_bar
except Exception as e:
    pages_ok = False
    data_error = f"Erreur import pages: {e}"
    print(f"⚠️ {data_error}")

# =============================
# LAYOUT
# =============================
def layout_ok():
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            create_nav_bar(),
            html.Div(id="page-content"),
            # interval = 2s pour déclencher le chargement côté callback sans bloquer le premier rendu
            dcc.Interval(id="data-check", interval=2000, n_intervals=0),
        ]
    )

def layout_error():
    return html.Div(
        style={"maxWidth": "900px", "margin": "40px auto", "fontFamily": "Arial"},
        children=[
            html.H1("Erreur de configuration"),
            html.Pre(str(data_error), style={"whiteSpace": "pre-wrap", "color": "crimson"}),
            html.P("Vérifie les imports dans pages/ et les chemins de fichiers."),
        ],
    )

app.layout = layout_ok() if pages_ok else layout_error()

# =============================
# CHARGEMENT DATA (1 seule fois)
# =============================
def load_data_once():
    """Charge les données une seule fois, thread-safe."""
    global data, data_loaded, data_error

    if data_loaded:
        return

    with _data_lock:
        if data_loaded:
            return

        try:
            from data_loader import load_all_data
            print("📂 Chargement des données (cache ou génération)…")
            data = load_all_data()
            data_loaded = True
            data_error = None
            print("✅ Données chargées.")
        except Exception as e:
            data_error = f"Erreur load_all_data(): {e}"
            print(f"❌ {data_error}")
            import traceback
            traceback.print_exc()

# =============================
# CALLBACK ROUTING
# =============================
if pages_ok:
    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname"), Input("data-check", "n_intervals")],
    )
    def display_page(pathname, n):
        # Tenter de charger sans bloquer un import global
        if not data_loaded and data_error is None:
            load_data_once()

        # Si erreur data
        if data_error is not None:
            return html.Div(
                style={"maxWidth": "900px", "margin": "40px auto", "fontFamily": "Arial"},
                children=[
                    html.H2("❌ Erreur lors du chargement des données"),
                    html.Pre(str(data_error), style={"whiteSpace": "pre-wrap", "color": "crimson"}),
                    html.P("Vérifie que les fichiers existent bien sur Render (data/...)."),
                ],
            )

        # Si data pas encore chargée
        if not data_loaded:
            return html.Div(
                style={"maxWidth": "900px", "margin": "40px auto", "fontFamily": "Arial"},
                children=[
                    html.H2("⏳ Chargement des données…"),
                    html.P("Cela peut prendre un peu de temps au premier démarrage."),
                    html.P("La page se mettra à jour automatiquement."),
                ],
            )

        # Routing
        if pathname == "/page1":
            return page1.layout
        elif pathname == "/page2":
            return page2.layout
        elif pathname == "/page3":
            return page3.layout
        elif pathname == "/page4":
            return page4.layout
        else:
            return home.layout

# =============================
# LOCAL ONLY
# =============================
if __name__ == "__main__":
    # Render utilise gunicorn, donc ce bloc est uniquement pour local.
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050)),
        debug=False
    )
