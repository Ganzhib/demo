import json
import os

class FileHandler:
    def __init__(self):
        # Get the path to the novel_generator package root
        self.root_path = os.path.dirname(os.path.dirname(__file__))

    def _get_absolute_path(self, filename):
        return os.path.join(self.root_path, filename)

    def save_json_to_file(self, data, filename):
        full_path = self._get_absolute_path(filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def read_json_from_file(self, filename):
        full_path = self._get_absolute_path(filename)
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_text_to_file(self, content, filename):
        full_path = self._get_absolute_path(filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def read_text_from_file(self, filename):
        full_path = self._get_absolute_path(filename)
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
