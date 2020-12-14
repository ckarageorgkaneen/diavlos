import os

class DataUtil:

    def __init__(self, filepath):
        self._dirname = os.path.dirname(filepath)

    def _input_dir(self, dir_):
        return os.path.join(self._dirname, dir_)

    def files_with_extension(self, dir_, extension):
        input_dir = self._input_dir(dir_)
        return {os.path.splitext(file)[0]: os.path.join(input_dir, file)
                for file in os.listdir(input_dir) if file.endswith(
                    f'.{extension}')}
