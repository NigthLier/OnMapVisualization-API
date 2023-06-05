import yaml


class Map:
    def __init__(self, file_path):
        self.data = None

        with open(file_path, 'r') as file:
            content = file.read()
        output_filename = 'modified.yaml'
        modified_content = content.replace(':', ': ')
        with open(output_filename, 'w') as file:
            file.write(modified_content)
        with open(output_filename, 'r') as file:
            lines = file.readlines()
        modified_lines = lines[2:]
        with open(output_filename, 'w') as file:
            file.writelines(modified_lines)

        with open(output_filename, 'r') as f:
            self.data = yaml.safe_load(f)
        types = set()
        for obj in self.data['GeoMapObjects']:
            types.add(obj['type'])
        print(*types)

        '''for obj_data in data['GeoMapObjects']:
            obj = {
                'idx': obj_data['idx'],
                'type': obj_data['type'],
                'pts': obj_data['pts'],
                'tags': obj_data['tags'],
                'layer': obj_data['layer'],
                'lastModified': obj_data['lastModified']
            }
            self.objects.append(obj)'''

    def get_objects(self):
        return self.data

    def get_objects_by_type(self, obj_type):
        return [obj for obj in self.data if obj['type'] == obj_type]

    def get_object_by_id(self, obj_id):
        for obj in self.data:
            if obj['idx'] == obj_id:
                return obj
        return None

    def get_objects_by_bbox(self, bbox):
        min_x, min_y, max_x, max_y = bbox
        objects_within_bbox = []
        for obj in self.data:
            pts = obj['pts']
            x_coordinates = pts[::2]
            y_coordinates = pts[1::2]
            if all(min_x <= x <= max_x for x in x_coordinates) and all(min_y <= y <= max_y for y in y_coordinates):
                objects_within_bbox.append(obj)
        return objects_within_bbox

    def change_object_attributes(self, obj_id, attributes):
        for obj in self.data:
            if obj['idx'] == obj_id:
                for attr, value in attributes.items():
                    if attr in obj:
                        obj[attr] = value
                    else:
                        raise ValueError(f"Attribute '{attr}' does not exist for object with ID '{obj_id}'.")
                return
        raise ValueError(f"No object found with ID '{obj_id}'.")

    def add_new_object(self, obj_type, attributes):
        duplicate_objects = [obj for obj in self.data if obj['type'] == obj_type and all(obj[attr] == value for attr, value in attributes.items())]
        if duplicate_objects:
            raise ValueError("Object with the same attributes already exists.")

        new_object = {
            'idx': None,
            'type': obj_type,
            'pts': [],
            'tags': {},
            'layer': '',
            'lastModified': ''
        }

        for attr, value in attributes.items():
            if attr in new_object:
                new_object[attr] = value
            else:
                raise ValueError(f"Attribute '{attr}' is not valid for object type '{obj_type}'.")

        self.data.append(new_object)

        return new_object

    def save_map(self, file_path):
        with open(file_path, 'w') as f:
            yaml.dump(self.data, f)


map_instance = Map('geomap.yaml')
