import dash
from dash import dcc
from dash import html
import dash_leaflet as dl
from dash.dependencies import Input, Output, State
from Map import Map

app = dash.Dash(__name__, suppress_callback_exceptions=True)
map_instance = Map('geomap.yaml')

app.layout = html.Div([
    html.H1("Interactive Map Board"),

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
        dcc.Input(id='new-object', type='text', placeholder='New Object'),
        html.Button('Add Object', id='add-btn', n_clicks=0),
        html.Div(id='add-status')
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H2("Save Map"),
        dcc.Input(id='filename-input', type='text', placeholder='File name'),
        html.Button('Save Map', id='save-button', n_clicks=0),
        html.Div(id='add-status')
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H2("Select Resource"),
        dcc.Dropdown(
            id='resource-dropdown',
            options=[
                {'label': 'Leaflet', 'value': 'resource1'},
                {'label': 'Google', 'value': 'resource2'},
                {'label': '2ГИС', 'value': 'resource3'}
            ],
            value='resource1'
        )
    ], style={'margin-bottom': '20px'}),

    html.Div(id='map-container')
])

@app.callback(
    dash.dependencies.Output('map-container', 'children'),
    [dash.dependencies.Input('resource-dropdown', 'value')]
)
def update_resource(resource):
    if resource == 'resource1':
        return dl.Map(
            id='map',
            center=[5.9841484199999996e+01, 3.0484612680000001e+01],
            zoom=10,
            children=[
                dl.LayerGroup(id='map-group'),
                dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
            ],
            style={'width': '100%', 'height': '500px'}
        )
    elif resource == 'resource2':
        return dl.Map(
            id='map',
            center=[5.9841484199999996e+01, 3.0484612680000001e+01],
            zoom=10,
            children=[
                dl.LayerGroup(id='map-group'),
                dl.TileLayer(url="http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}")
            ],
            style={'width': '100%', 'height': '500px'}
        )
    elif resource == 'resource3':
        return dl.Map(
            id='map',
            center=[5.9841484199999996e+01, 3.0484612680000001e+01],
            zoom=10,
            children=[
                dl.LayerGroup(id='map-group'),
                dl.TileLayer(url="http://tile2.maps.2gis.com/tiles?x={x}&y={y}&z={z}")
            ],
            style={'width': '100%', 'height': '500px'}
        )


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
    Output('map-group', 'children'),
    [Input('resource-dropdown', 'value')]
)
def update_map(resource):
    markers = []
    colors = {
        'AGM_Curb': 'gold',
        'AGM_CurbEdge': 'orange',
        'AGM_StopShelter': 'red',
        'AGM_SingleRail': 'green',
        'AGM_TrafficLight': 'violet',
        'AGM_Pole': 'blue'
    }
    objects = map_instance.get_objects()
    for obj in objects['GeoMapObjects']:
        if not obj['type'] in ['AGM_RoadNode', 'AGM_Rails', 'AGM_ExternalRailPropertises']:
            positions = []
            for i in range(0, len(obj['pts']), 2):
                positions.append([obj['pts'][i+1], obj['pts'][i]])
            if obj['type'] in ['AGM_StopShelter', 'AGM_TrafficLight', 'AGM_Pole', 'AGM_Curb']:
                markers.append(dl.Polygon(positions=positions, children=dl.Tooltip(obj['type']+str(obj['idx'])), color=colors[obj['type']]))
            if obj['type'] in ['AGM_SingleRail', 'AGM_CurbEdge']:
                markers.append(dl.Polyline(positions=positions, children=dl.Tooltip(obj['type']+str(obj['idx'])), color=colors[obj['type']]))
    return markers


@app.callback(
    dash.dependencies.Output('save-button', 'n_clicks'),
    [dash.dependencies.Input('save-button', 'n_clicks')],
    [dash.dependencies.State('filename-input', 'value')]
)
def save_map(n_clicks, filename):
    if n_clicks > 0 and filename:
        file_path = f"{filename}.yaml"
        Map.save_map(map_instance, file_path)
        print(f"Map data saved to file: {file_path}")

    return 0


if __name__ == '__main__':
    app.run_server(debug=True)
