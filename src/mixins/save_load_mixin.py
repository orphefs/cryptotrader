import dill

dill.dill._reverse_typemap['ClassType'] = type
import os
from src import definitions
import simplejson as json


class DillSaveLoadMixin:
    def save_to_disk(self, path_to_file: str):
        if not os.path.isabs(path_to_file):
            path_to_file = os.path.join(definitions.DATA_DIR, path_to_file)
        with open(os.path.join(definitions.DATA_DIR, path_to_file), 'wb') as outfile:
            dill.dump(self, outfile)

    @staticmethod
    def load_from_disk(path_to_file: str):
        if not os.path.isabs(path_to_file):
            path_to_file = os.path.join(definitions.DATA_DIR, path_to_file)
        with open(path_to_file, 'rb') as outfile:
            obj = dill.load(outfile)
        return obj


class JsonSaveMixin:
    def save_to_disk(self, path_to_file: str):
        if not os.path.isabs(path_to_file):
            path_to_file = os.path.join(definitions.DATA_DIR, path_to_file)
        with open(os.path.join(definitions.DATA_DIR, path_to_file), 'wb') as outfile:
            data = json.dumps(self, default=convert_to_dict, indent=4, sort_keys=True)
            outfile.writelines(data)


def convert_to_dict(obj):
    """
    A function takes in a custom object and returns a dictionary representation of the object.
    This dict representation includes meta data such as the object's module and class names.
    """
    #  Populate the dictionary with object meta data
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }
    #  Populate the dictionary with object properties
    obj_dict.update(obj.__dict__)

    return obj_dict
