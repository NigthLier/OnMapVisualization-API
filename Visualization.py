import dash
from dash import dcc
from dash import html
import dash_leaflet as dl
from dash.dependencies import Input, Output, State
from Map import Map

app = dash.Dash(__name__, suppress_callback_exceptions=True)
map_instance = Map('geomap.yaml')
Objects = {'GeoMapObjects': []}

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
        html.Div(id='save-status')
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H2("Show all"),
        html.Button('Show all', id='all-map-button', n_clicks=0),
        html.Div(id='all-map-status')
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H2("Find by Id"),
        dcc.Input(id='id-input', type='text', placeholder='ID'),
        html.Button('Find', id='id-map-button', n_clicks=0),
        html.Div(id='id-map-status')
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H2("Find by type"),
        dcc.Input(id='type-input', type='text', placeholder='type'),
        html.Button('Find', id='type-map-button', n_clicks=0),
        html.Div(id='type-map-status')
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H2("Find in box"),
        dcc.Input(id='bbox-x1-input', type='text', placeholder='x1'),
        dcc.Input(id='bbox-y1-input', type='text', placeholder='y1'),
        dcc.Input(id='bbox-x2-input', type='text', placeholder='x2'),
        dcc.Input(id='bbox-y2-input', type='text', placeholder='y2'),
        html.Button('Find', id='bbox-map-button', n_clicks=0),
        html.Div(id='bbox-map-status')
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
    Output('map-container', 'children'),
    [Input('resource-dropdown', 'value')]
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
        success = map_instance.change_object_attributes(object_id, {attribute_name: float(new_value)})
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
    
    if n_clicks > 0 and new_object:
        elem = new_object.split(' ', 1)
        type = elem[0]
        attributes = elem[1]
        success = map_instance.add_new_object(type, [float(i) for i in attributes.split(',')])
        if success:
            return html.Div('New object added successfully.')
        else:
            return html.Div(
                'Failed to add new object. Please check the input value and ensure there are no duplications.')
    return ''


@app.callback(
    Output('map-group', 'children'),
    [Input('resource-dropdown', 'value')],
    [Input('all-map-button', 'n_clicks')],
    [Input('id-map-button', 'n_clicks')],
    [Input('type-map-button', 'n_clicks')],
    [Input('bbox-map-button', 'n_clicks')],
    [Input('update-btn', 'n_clicks')],
    [Input('add-btn', 'n_clicks')]
)
def update_map(resource, all, id, type, bbox, upd, add):
    markers = []
    colors = {
        'AGM_Curb': 'gold',
        'AGM_CurbEdge': 'orange',
        'AGM_StopShelter': 'red',
        'AGM_SingleRail': 'green',
        'AGM_TrafficLight': 'violet',
        'AGM_Pole': 'blue'
    }
    weight = {
        'AGM_Curb': 3,
        'AGM_CurbEdge': 2,
        'AGM_StopShelter': 3,
        'AGM_SingleRail': 3,
        'AGM_TrafficLight': 6,
        'AGM_Pole': 6
    }
    for obj in Objects['GeoMapObjects']:
        if not obj['type'] in ['AGM_RoadNode', 'AGM_Rails', 'AGM_ExternalRailPropertises']:
            positions = []
            for i in range(0, len(obj['pts']), 2):
                positions.append([obj['pts'][i+1], obj['pts'][i]])
            if obj['type'] in ['AGM_StopShelter', 'AGM_TrafficLight', 'AGM_Pole']:
                markers.append(dl.Polygon(positions=positions, children=dl.Tooltip(obj['type']+str(obj['idx'])), color=colors[obj['type']], weight=weight[obj['type']]))
            if obj['type'] in ['AGM_SingleRail', 'AGM_CurbEdge', 'AGM_Curb']:
                markers.append(dl.Polyline(positions=positions, children=dl.Tooltip(obj['type']+str(obj['idx'])), color=colors[obj['type']], weight=weight[obj['type']]))
    return markers


@app.callback(
    Output('save-button', 'n_clicks'),
    [Input('save-button', 'n_clicks')],
    [State('filename-input', 'value')]
)
def save_map(n_clicks, filename):
    if n_clicks > 0 and filename:
        file_path = f"{filename}.yaml"
        Map.save_map(map_instance, file_path)
        print(f"Map data saved to file: {file_path}")

    return 0

@app.callback(
    Output('all-map-button', 'n_clicks'),
    [Input('all-map-button', 'n_clicks')],
)
def all_map(n_clicks):
    if n_clicks > 0:
        Objects['GeoMapObjects'] = map_instance.get_objects()
    return 0

@app.callback(
    Output('id-map-button', 'n_clicks'),
    [Input('id-map-button', 'n_clicks')],
    [State('id-input', 'value')]
)
def find_id_map(n_clicks, id):
    if n_clicks > 0 and id:
        Objects['GeoMapObjects'] = [map_instance.get_object_by_id(int(id))]
    return 0

@app.callback(
    Output('type-map-button', 'n_clicks'),
    [Input('type-map-button', 'n_clicks')],
    [State('type-input', 'value')]
)
def find_type_map(n_clicks, type):
    if n_clicks > 0 and type:
        Objects['GeoMapObjects'] = map_instance.get_objects_by_type(type)
    return 0

@app.callback(
    Output('bbox-map-button', 'n_clicks'),
    [Input('bbox-map-button', 'n_clicks')],
    [State('bbox-x1-input', 'value')],
    [State('bbox-y1-input', 'value')],
    [State('bbox-x2-input', 'value')],
    [State('bbox-y2-input', 'value')]
)
def find_type_map(n_clicks, x1, y1, x2, y2):
    if n_clicks > 0 and x1 and x2 and y1 and y2:
        Objects['GeoMapObjects'] = map_instance.get_objects_by_bbox([float(x1),float(y1),float(x2),float(y2)])
    return 0

if __name__ == '__main__':
    app.run_server(debug=True)
