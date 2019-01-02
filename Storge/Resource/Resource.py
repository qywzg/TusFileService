"""医学图像上传与处理服务"""
from sanic.exceptions import NotFound, ServerError
from sanic import Sanic, response
import aiofiles
import json
import os

app = Sanic()
StorgePath = '/storge/'



def get_path_by(indentifier):
    file_dir = os.path.join(StorgePath, indentifier)
    metadata = None
    for file in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file)
        if file.startswith('metadata') and not file.startswith('.'):
            with open(file_path, 'r') as metadata_file:
                metadata = json.loads(metadata_file.read())
    if metadata:
        filename = metadata.get('filename', metadata.get('Filename', None))
        indentifier = metadata.get('indentifier', metadata.get('Indentifier', None))
        if indentifier == indentifier:
            return os.path.join(file_dir, filename)
    else:
        raise Exception('No metadata file found, Can not read the file useing indentifier, please see Storge:get_path_by:indentifier function')

def get_filename_by(indentifier):
    file_dir = os.path.join(StorgePath, indentifier)
    metadata = None
    for file in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file)
        if file.startswith('metadata') and not file.startswith('.'):
            with open(file_path, 'r') as metadata_file:
                metadata = json.loads(metadata_file.read())
    if metadata:
        filename = metadata.get('filename', metadata.get('Filename', None))
        indentifier = metadata.get('indentifier', metadata.get('Indentifier', None))
        if indentifier == indentifier:
            return filename
    else:
        raise Exception('No metadata file found, Can not read the file useing indentifier, please see Storge:get_path_by:indentifier function')


@app.route("storge/resource/<indentifier>", methods=['GET'])
async def resource(request, indentifier):
    return await response.file_stream(get_path_by(indentifier), filename=get_filename_by(indentifier), chunk_size=1024 * 1024)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8880)