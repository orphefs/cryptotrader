import dill

from src.type_aliases import Path

dill.dill._reverse_typemap['ClassType'] = type
import os
from src import definitions
import simplejson as json


def verify_if_extension(path_to_file: Path, desired_extension: str) -> Path:
    if os.path.splitext(path_to_file)[1] == "":  # has no extension
        path_to_file += desired_extension
    elif os.path.splitext(path_to_file)[1] != desired_extension:
        path_to_file = os.path.splitext(path_to_file)[0] + desired_extension
    return path_to_file


def convert_to_absolute_path(path_to_file: Path) -> Path:
    if not os.path.isabs(path_to_file):
        path_to_file = os.path.join(definitions.DATA_DIR, path_to_file)
    return path_to_file


class DillSaveLoadMixin:
    @staticmethod
    def save_to_disk(obj, path_to_file: Path):
        path_to_file = verify_if_extension(path_to_file, ".dill")
        path_to_file = convert_to_absolute_path(path_to_file)
        with open(os.path.join(definitions.DATA_DIR, path_to_file), 'wb') as outfile:
            dill.dump(obj, outfile)

    @staticmethod
    def load_from_disk(path_to_file: Path):
        path_to_file = convert_to_absolute_path(path_to_file)
        with open(path_to_file, 'rb') as outfile:
            obj = dill.load(outfile)
        return obj


class JsonSaveMixin:
    @staticmethod
    def save_to_disk(obj, path_to_file: str):
        path_to_file = verify_if_extension(path_to_file, ".json")
        path_to_file = convert_to_absolute_path(path_to_file)
        with open(os.path.join(definitions.DATA_DIR, path_to_file), 'wb') as outfile:
            # json.dump(obj, outfile, default=convert_to_dict, indent=4, sort_keys=True)
            print("Supposedly saving to JSON...")

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
