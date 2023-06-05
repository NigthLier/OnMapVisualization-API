import dash
from dash import dcc
from dash import html
import dash_leaflet as dl
from dash.dependencies import Input, Output, State

from Map import Map

app = dash.Dash(__name__, suppress_callback_exceptions=True)
map_instance = Map('geomap.yaml')

app.layout = html.Div([
    html.H1("Interactive Board with Google Street View"),

    html.Div([
        html.H2("Update Object Attribute"),
        dcc.Input(id='object-id', type='number', placeholder='Object ID'),
        dcc.Input(id='attribute-name', type='text', placeholder='Attribute Name'),
        dcc.Input(id='new-value', type='text', placeholder='New Value'),
        html.Button('Update Attribute', id='update-btn', n_clicks=0),
        html.Div(id='update-status')
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H2("Add New Object"),
        dcc.Input(id='new-object', type='text', placeholder='New Object JSON'),
        html.Button('Add Object', id='add-btn', n_clicks=0),
        html.Div(id='add-status')
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H2("Select Resource"),
        dcc.Dropdown(
            id='resource-dropdown',
            options=[
                {'label': 'Resource 1', 'value': 'resource1'},
                {'label': 'Resource 2', 'value': 'resource2'},
                {'label': 'Resource 3', 'value': 'resource3'}
            ],
            value='resource1'
        )
    ], style={'margin-bottom': '20px'}),

    dl.Map(
        id='map',
        center=[51.505, -0.09],
        zoom=10,
        children=[
            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
            dl.LayerGroup(id='marker-group')
        ],
        style={'width': '100%', 'height': '500px'}
    )
])


@app.callback(
    Output('update-status', 'children'),
    [Input('update-btn', 'n_clicks')],
    [State('object-id', 'value'),
     State('attribute-name', 'value'),
     State('new-value', 'value')]
)
def update_object_attribute(n_clicks, object_id, attribute_name, new_value):
    if n_clicks > 0:
        success = map_instance.change_object_attributes(object_id, {attribute_name: new_value})
        if success:
            return html.Div('Attribute updated successfully.')
        else:
            return html.Div('Failed to update attribute. Please check the input values.')
    return ''


@app.callback(
    Output('object-layer', 'options'),
    [Input('resource-dropdown', 'value')]
)
def update_street_view_layer(resource):
    if resource == 'resource1':
        return {'source': 'resource1_url'}
    elif resource == 'resource2':
        return {'source': 'resource2_url'}
    elif resource == 'resource3':
        return {'source': 'resource3_url'}
    else:
        return {}


@app.callback(
    Output('selected-resource', 'children'),
    [Input('resource-dropdown', 'value')]
)
def display_selected_resource(resource):
    return f"You selected: {resource}"


@app.callback(
    Output('add-status', 'children'),
    [Input('add-btn', 'n_clicks')],
    [State('new-object', 'value')]
)
def add_new_object(n_clicks, new_object):
    if n_clicks > 0:
        success = map_instance.add_new_object(new_object)
        if success:
            return html.Div('New object added successfully.')
        else:
            return html.Div(
                'Failed to add new object. Please check the input value and ensure there are no duplications.')
    return ''


@app.callback(
    Output('marker-group', 'children'),
    [Input('resource-dropdown', 'value')]
)
def update_map_markers(resource):
    markers = []
    objects = map_instance.get_objects()
    for obj in objects['GeoMapObjects']:
        x_values = obj['pts'][0]
        y_values = obj['pts'][1]
        if obj['type'] == 'AGM_TrafficLight':
            markers.append(dl.Marker(position=[x_values, y_values], children=dl.Tooltip(obj['type'])))
    return markers


if __name__ == '__main__':
    app.run_server(debug=True)