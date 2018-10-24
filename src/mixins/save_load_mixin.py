import dill
import os
from src import definitions


class DillSaveLoadMixin:
    def save_to_disk(self, path_to_file: str):
        with open(os.path.join(definitions.DATA_DIR, path_to_file), 'wb') as outfile:
            dill.dump(self, outfile)

    @staticmethod
    def load_from_disk(path_to_file: str):
        with open(os.path.join(definitions.DATA_DIR, path_to_file), 'rb') as outfile:
            obj = dill.load(outfile)
        return obj