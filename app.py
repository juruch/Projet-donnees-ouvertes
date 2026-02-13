import os
import threading

import dash
from dash import dcc, html, Input, Output

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

@server.route("/healthz")
def healthz():
    return "ok", 200

# ===== ETAT GLOBAL =====
data = None
data_loaded = False
data_error = None
_data_lock = threading.Lock()

# ===== IMPORT PAGES =====
try:
    from pages import home, page1, page2, page3, page4
    from pages.navigation import create_nav_bar
    pages_ok = True
except Exception as e:
    pages_ok = False
    data_error = f"Erreur import pages: {e}"
    print(f"⚠️ {data_error}")

# ===== LAYOUT =====
if pages_ok:
    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        create_nav_bar(),
        html.Div(id="page-content"),
        dcc.Interval(id="data-check", interval=1500, n_intervals=0)
    ])
else:
    app.layout = html.Div([
        html.H1("Erreur de configuration"),
        html.Pre(str(data_error), style={"whiteSpace": "pre-wrap", "color": "crimson"})
    ])

def load_data_once():
    global data, data_loaded, data_error
    if data_loaded:
        return
    with _data_lock:
        if data_loaded:
            return
        try:
            from data_loader import load_all_data
            print("📂 Chargement des données...")
            data = load_all_data()
            data_loaded = True
            data_error = None
            print("✅ Données chargées.")
        except Exception as e:
            data_error = f"Erreur load_all_data(): {e}"
            print(f"❌ {data_error}")
            import traceback
            traceback.print_exc()

# util: appelle layout() si c'est une fonction
def render_page(module):
    lay = getattr(module, "layout", None)
    if lay is None:
        return html.Div([html.H2("Page invalide"), html.P("Aucun layout trouvé.")])
    return lay(data) if callable(lay) else lay

if pages_ok:
    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname"), Input("data-check", "n_intervals")]
    )
    def display_page(pathname, n):
        if not data_loaded and data_error is None:
            load_data_once()

        if data_error is not None:
            return html.Div([
                html.H2("❌ Erreur lors du chargement des données"),
                html.Pre(str(data_error), style={"whiteSpace": "pre-wrap", "color": "crimson"})
            ])

        if not data_loaded:
            return html.Div([
                html.H2("⏳ Chargement des données..."),
                html.P("Veuillez patienter (premier démarrage).")
            ])

        if pathname == "/page1":
            return render_page(page1)
        elif pathname == "/page2":
            return render_page(page2)
        elif pathname == "/page3":
            return render_page(page3)
        elif pathname == "/page4":
            return render_page(page4)
        else:
            return render_page(home)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)
