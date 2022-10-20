
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

def get_objects(chain):
    return list(chain.objects.keys())

def get_relations(chain):
    return list(chain.actions.keys())

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

def new_trans_modal():
    return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New Transaction")),
                dbc.ModalBody(
                    html.Div([
                        dcc.Dropdown(
                            id="trans_from",
                            options=[dict(label=mychain.get_name(o), value=o) for o in get_objects(mychain)],
                        ),
                        dcc.Dropdown(
                            id="trans_rel",
                            options=[dict(label=mychain.get_name(o), value=o) for o in get_relations(mychain)],
                        ),
                        dcc.Dropdown(
                            id="trans_to",
                            options=[dict(label=mychain.get_name(o), value=o) for o in get_objects(mychain)],
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
                dcc.RadioItems(['User', 'Asset', 'Action'], 'Asset', inline=True, id="object-type"),
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
    [
        Output("memory", "data"),
        Output("graphs", "children"),
        Output("new-trans-div", "children"),
    ],
    [
        Input("create-trans-button", "n_clicks"),
        Input("create-user-button", "n_clicks"),
        Input("publish-pending","n_clicks")
    ],
    [
        State("trans_from", "value"),
        State("trans_to", "value"),
        State("trans_rel", "value"),
        State("friendly-name", "value"),
        State("object-type", "value"),
        State("memory", 'data')
    ]
)
def create_trans_form(trans_button, user_button, publish_button, frm, to, rel, name, objtype, data):
    data = data or []

    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'create-trans-button':
        data += [(frm, to, rel)]
    elif button_id == 'create-user-button':
        new_user = Node()
        data += [(new_user.id, new_user.id, {'name': name,'type':objtype})]
    elif button_id == 'publish-pending':
        mychain.add_block(data)
        data = []
    return data, draw_graphs(), new_trans_modal()


@app.callback(
    Output("pending-transactions", "children"),
    [Input("memory", 'data')],
    []
)
def update_pending(data):
    data = data or []
    return [dbc.ListGroupItem(f"{t[0]},{t[1]},{t[2]}") for t in data]


def draw_graphs():
    return [
        html.Table([
            html.Thead(
                html.Tr(
                    [html.Td(
                        html.H3("Graph")
                    ),
                    html.Td(
                        html.H3("Block Chain")
                    )]
                )
            ),
            html.Tbody(
                html.Tr([
                    html.Td(
                        cyto.Cytoscape(
                            id='Graph',
                            elements=output(mychain, mode='cytograph'),
                            layout={'name': 'breadthfirst'},
                            # style={'width': '400px', 'height': '500px'},
                            stylesheet=[
                            {
                                'selector': 'node',
                                'style': {
                                    'content': 'data(label)'
                                }
                            },
                            {
                                'selector': 'edge',
                                'style': {
                                    'label': 'data(label)'
                                }
                            },
                            ]
                        ),
                    style={'width': '50%','border': 'solid'}),
                    html.Td(
                        cyto.Cytoscape(
                            id='Chain',
                            elements=output(mychain, mode='cytochain'),
                            layout={'name': 'grid'},
                            # style={'width': '400px', 'height': '500px'}
                        ),
                        style={'width': '50%','border': 'solid'}
                    )
                ])
            )
        ])
        
        
    ]

  
app.layout = html.Div([
    html.Div([
        html.H2("Create transactions"),
        dbc.Row([
            dbc.Col([
                dbc.Button("Add Object",  id="add-user-button",  color="primary"),
                dbc.Button("Add Relation", id="add-trans-button", color="primary")
            ]),
            dcc.Store(id='memory'),
            dbc.Col([
                dbc.ListGroup(id='pending-transactions',
                    children = []
                ),
                dbc.Button("Publish", id="publish-pending", color="primary")
            ])
        ]),
        html.Div(new_user_modal(),id='new-user-div'),
        html.Div(new_trans_modal(),id='new-trans-div')

    ]),
    html.Div([
        html.Div(draw_graphs(), id='graphs')
        
    ],
    )
])


if __name__ == '__main__':
    app.run_server(host='0.0.0.0')