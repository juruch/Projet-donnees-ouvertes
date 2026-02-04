import dash
from dash import dcc, html

# Enregistrement de la page
dash.register_page(__name__, path='/')



layout = html.Div(
    style={
        #'backgroundColor': '#0b2272',  # Couleur de fond de la page
        'height': '100vh',  # Hauteur de la page pour remplir l'écran
        'padding': '20px',  # Padding autour du contenu
        'display': 'flex',  # Utilisation de flexbox pour centrer le contenu
        'flexDirection': 'column',  # Disposition en colonne
    },
    children=[
        html.Div(
            style={
                'border': '2px solid #53555c',  # Bordure autour du titre
                'padding': '10px',  # Espacement à l'intérieur de la bordure
                'borderRadius': '5px',  # Coins arrondis
                'backgroundColor': '#cbcccf',  # Couleur de fond à l'intérieur de la bordure
                'textAlign': 'center'  # Centrer le texte
            },
            children=[
                html.H1(
                    children='CECI EST NOTRE PROBLÉMATIQUE',
                    style={'margin': '0'}  # Supprimer la marge par défaut
                )
            ]
        ),
        html.P(
            'Ceci est la page d\'accueil de votre application.'
        )
    ]
)
