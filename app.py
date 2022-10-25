
# importing required libraries
from uuid import uuid4
import dash
from dash import dcc, html, Input, Output, State

# import dash_interactive_graphviz
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

from chain import output, Chain, toYaml, toJson, fromTxt

def get_objects(chain):
    return list(chain.objects.keys())

def get_relations(chain):
    return list(chain.actions.keys())

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

def new_trans_modal(mychain):
    try:
        objects = [dict(label=mychain.get_name(o), value=o) for o in get_objects(mychain)]
        relations = [dict(label=mychain.get_name(o), value=o) for o in get_relations(mychain)]
    except:
        objects = []
        relations = []

    return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New Transaction")),
                dbc.ModalBody(
                    html.Div([
                        dcc.Dropdown(
                            id="trans_from",
                            options=objects,
                        ),
                        dcc.Dropdown(
                            id="trans_rel",
                            options=relations,
                        ),
                        dcc.Dropdown(
                            id="trans_to",
                            options=objects,
                        ),
                        
                        dbc.Button("Create", id="create-trans-button", color="primary")
                    ])
                ),
            ],
            id="new-trans-modal",
            is_open=False,
        )
def load_save_modal():
    return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("YAML")),
                dbc.ModalBody(
                    html.Div([
                        dbc.Textarea(id='output-text'),
                        dbc.Button("Save", id="load-yaml", color="primary")
                    ])
                )
            ],
            id="load-save-modal",
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
                        dbc.Button("Create", id="create-obj-button", color="primary")
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
    Output("load-save-modal", "is_open"),
    [Input("save-load-button", "n_clicks")],
    [State("load-save-modal", "is_open")]
)
def open_save_modal(button, is_open):
    if button:
        return not is_open
    return is_open

@app.callback(
    [
        Output("memory", "data"),
        Output("graphs", "children"),
        Output("new-trans-div", "children"),
        Output("output-text", "value")
    ],
    [
        Input("create-trans-button", "n_clicks"),
        Input("create-obj-button", "n_clicks"),
        Input("publish-pending","n_clicks"),
        Input("load-yaml","n_clicks"),
    ],
    [
        State("trans_from", "value"),
        State("trans_to", "value"),
        State("trans_rel", "value"),
        State("friendly-name", "value"),
        State("object-type", "value"),
        State("output-text", "value"),
        State("memory", 'data')
    ]
)
def create_trans_form(
    trans_button, 
    user_button, 
    publish_button, 
    load_button, 
    frm, 
    to, 
    rel, 
    name, 
    objtype, 
    loadtext, 
    data
    ):
    if not data: data={}
    pending = data.get('pending',[])
    mychain = fromTxt(data.get('chain', []))

    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'create-trans-button':
        pending += [(frm, to, rel)]
    elif button_id == 'create-obj-button':
        uid = uuid4().hex
        pending += [(uid, uid, {'name': name,'type':objtype})]
    elif button_id == 'publish-pending':
        if pending:
            mychain.add_block(transactions=pending)
        pending = []
    elif button_id == 'load-yaml':
        txt = loadtext
        newchain = fromTxt(loadtext)
        if isinstance(newchain, Chain):
            mychain = newchain
        pending = []
    data['pending'] = pending
    data['chain'] = toJson(mychain)
    return data, draw_graphs(mychain), new_trans_modal(mychain), toYaml(mychain)


@app.callback(
    Output("pending-transactions", "children"),
    [Input("memory", 'data')],
    []
)
def update_pending(data):
    data = data.get('pending', [])
    return [dbc.ListGroupItem(f"{t[0]},{t[1]},{t[2]}") for t in data]


def draw_graphs(mychain):
    if not mychain:
        return [html.H1("NO DATA YET")]
    content = [
        dbc.Button("SAVE/LOAD",  id="save-load-button",  color="primary")
    ]
    if mychain:
        content += [cyto.Cytoscape(
            id='Chain',
            elements=output(mychain, mode='cytochain'),
            layout={'name': 'breadthfirst'},
            style={'width': '1000px', 'height': '400px'},
        )]
        content += [cyto.Cytoscape(
            id='Graph',
            elements=output(mychain, mode='cytograph'),
            layout={'name': 'cose'},
            style={'width': '1000px', 'height': '1000px'},
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
        )]
    return content
  
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
        html.Div(load_save_modal(),id='load-save-div'),
        html.Div(new_user_modal(),id='new-user-div'),
        html.Div(new_trans_modal(None),id='new-trans-div')

    ]),
    html.Div([
        html.Div(draw_graphs(None), id='graphs')
        
    ],
    )
])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
