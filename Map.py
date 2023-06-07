import yaml


class Map:
    def __init__(self, file_path):
        self.data = None
        self.load_map(file_path)

    def load_map(self, file_path):
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

    def get_objects(self):
        return self.data['GeoMapObjects']

    def get_objects_by_type(self, obj_type):
        return [obj for obj in self.data['GeoMapObjects'] if obj['type'] == obj_type]

    def get_object_by_id(self, obj_id):
        for obj in self.data['GeoMapObjects']:
            if obj['idx'] == obj_id:
                return obj
        return None

    def get_objects_by_bbox(self, bbox):
        min_x, min_y, max_x, max_y = bbox
        objects_within_bbox = []
        for obj in self.data['GeoMapObjects']:
            pts = obj['pts']
            x_coordinates = pts[::2]
            y_coordinates = pts[1::2]
            if all(type(x) != str for x in x_coordinates) and all(type(y) != str for y in y_coordinates) and all(min_x <= x <= max_x for x in x_coordinates) and all(min_y <= y <= max_y for y in y_coordinates):
                objects_within_bbox.append(obj)
        return objects_within_bbox

    def change_object_attributes(self, obj_id, attributes):
        for obj in self.data['GeoMapObjects']:
            if obj['idx'] == obj_id:
                for attr, value in attributes.items():
                    if attr in obj:
                        obj[attr] = value
                    else:
                        raise ValueError(f"Attribute '{attr}' does not exist for object with ID '{obj_id}'.")
                return
        raise ValueError(f"No object found with ID '{obj_id}'.")

    def add_new_object(self, obj_type, attributes):
        new_object = {
            'idx': None,
            'type': obj_type,
            'pts': attributes
        }
        self.data['GeoMapObjects'].append(new_object)
        return new_object

    def save_map(self, file_path):
        with open(file_path, 'w') as f:
            yaml.dump(self.data, f)

