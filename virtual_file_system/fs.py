import fs

class SchemaFS():
    def __init__(self):
        self._fs_path = 'v://'
        self.fs = fs.open_fs(self._fs_path)
    

    def __enter__(self):
        return self.fs
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.fs.close()

    def open(self, file_path, mode='wb'):
        return self.fs.open(file_path, mode=mode)

    def write_file(file_path, data=None, **kwargs):
        with fs.open_fs('schemaTransfer://') as mem_fs:
            if data is not None:
                mem_fs.writetext(file_path, data)
            else:
                raise Exception('file content is empty')


    def read_file(file_path):
        with fs.open_fs('schemaTransfer://') as mem_fs:
            return mem_fs.readtext(file_path)