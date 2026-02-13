from dash import dcc, html


def create_nav_bar():
    nav_links = [
        {'label': 'Accueil', 'href': '/'},
        {'label': 'Département', 'href': '/page1'},
        {'label': 'Commune', 'href': '/page2'},
        {'label': 'Age', 'href': '/page3'},
        {'label': 'Prédiction', 'href': '/page4'},
    ]

    nav_bar = html.Div(
        style={'backgroundColor': '#007BFF', 'padding': '10px', 'color': 'white'},
        children=[
            html.Div(
                children=[
                    dcc.Link(
                        link['label'],
                        href=link['href'],
                        style={'color': 'white', 'margin': '0 15px', 'textDecoration': 'none'}
                    ) for link in nav_links
                ]
            )
        ]
    )
    return nav_bar