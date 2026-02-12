from dash import dcc, html


def create_nav_bar():
    nav_links = [
        {'label': 'Accueil', 'href': '/'},
        {'label': 'Page 1', 'href': '/page1'},
        {'label': 'Page 2', 'href': '/page2'},
        {'label': 'Page 3', 'href': '/page3'},
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