
# importing required libraries
import dash
from dash import dcc, html, Input, Output, State

# import dash_interactive_graphviz
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

from chain import *

users = []
pending = []

mychain = Chain()

user1 = User()
user2 = User()
asset1 = Asset()

mychain.add_block([
    (asset1.id, asset1.id, dict(url='mygitrepo/tag', sha='AAABBBCCCDDD')),
    (user1.id, asset1.id, Action.CREATED)
])
mychain.add_block([
    (user2.id, asset1.id, Action.USED)
])

def get_objects(chain):
    return ['111','222','333']

def get_relations(chain):
    return ['XXX','YYY','ZZZ']



app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

def new_trans_modal():
    return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New Transaction")),
                dbc.ModalBody(
                    html.Div([
                        dcc.Dropdown(
                            id="trans_from",
                            options=[dict(label=o, value=o) for o in get_objects(mychain)],
                        ),
                        dcc.Dropdown(
                            id="trans_to",
                            options=[dict(label=o, value=o) for o in get_objects(mychain)],
                        ),
                        dcc.Dropdown(
                            id="trans_rel",
                            options=[dict(label=o, value=o) for o in get_relations(mychain)],
                        ),
                        dbc.Button("Create", id="create-trans-button", color="primary")
                    ])
                ),
            ],
            id="new-trans-modal",
            is_open=False,
        )




def new_user_modal():
    return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New Object")),
                dbc.ModalBody(
                    html.Div([
                        dbc.Label("Name", html_for="new-user"),
                        dbc.Input(type="name", id="friendly-name", placeholder="Enter Friendly Name"),
                        dbc.Button("Create", id="create-user-button", color="primary")
                    ])
                ),
            ],
            id="new-user-modal",
            is_open=False,
        )
@app.callback(
    Output("new-user-modal", "is_open"),
    [Input("add-user-button", "n_clicks")],
    [State("new-user-modal", "is_open")]
)
def open_user_modal(button, is_open):
    if button:
        return not is_open
    return is_open

@app.callback(
    Output("new-trans-modal", "is_open"),
    [Input("add-trans-button", "n_clicks")],
    [State("new-trans-modal", "is_open")]
)
def open_trans_modal(button, is_open):
    if button:
        return not is_open
    return is_open


@app.callback(
    Output("memory", "data"),
    [
        Input("create-trans-button", "n_clicks"),
        Input("create-user-button", "n_clicks")
    ],
    [
        State("trans_from", "value"),
        State("trans_to", "value"),
        State("trans_rel", "value"),
        State("friendly-name", "value"),
        State("memory", 'data')
    ]
)
def create_trans_form(trans_button, user_button, frm, to, rel, name, data):
    data = data or []

    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'create-trans-button':
        data += [(frm, to, rel)]
    elif button_id == 'create-user-button':
        new_user = User()
        data += [(new_user.id, new_user.id, {'name': name})]
    return data


@app.callback(
    Output("pending-transactions", "children"),
    [Input("memory", 'data')],
    []
)
def update_pending(data):
    data = data or []
    return [dbc.ListGroupItem(f"{t[0]},{t[1]},{t[2]}") for t in data]


  
app.layout = html.Div([
    html.Div([
        html.H2("Create transactions"),
        dbc.Row([
            dbc.Col([
                dbc.Button("Add User/Asset",  id="add-user-button",  color="primary"),
                dbc.Button("Add Trans", id="add-trans-button", color="primary")
            ]),
            dcc.Store(id='memory'),
            dbc.Col([
                dbc.ListGroup(id='pending-transactions',
                    children = []
                ) 
            ])
        ]),
        new_user_modal(),
        new_trans_modal()

    ]),
    html.Div([
        html.H2("Show Chain & Graph"),
        cyto.Cytoscape(
            id='Graph',
            elements=output(mychain, mode='cytograph'),
            layout={'name': 'breadthfirst'},
            style={'width': '400px', 'height': '500px'}
        ),
        cyto.Cytoscape(
            id='Chain',
            elements=output(mychain, mode='cytochain'),
            layout={'name': 'breadthfirst'},
            style={'width': '400px', 'height': '500px'}
        ),
    ],
    style=dict(display="flex")
    )
])


if __name__ == '__main__':
    app.run_server()