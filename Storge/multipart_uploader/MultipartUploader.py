"""医学图像上传与处理服务"""
from multipart import FormParser, create_form_parser
from sanic.exceptions import NotFound, ServerError
from sanic import Sanic, response
from io import BytesIO
import requests
import aiofiles
import json
import uuid
import math
import os

app = Sanic()
app.config.REQUEST_MAX_SIZE = 50000000000  # in bytes
app.config.REQUEST_TIMEOUT = 60  # in secs
StorgePath = './storge/'


@app.post("storge/multipart", stream=True)
async def multipart_upload(request):
    storge_base = StorgePath

    async def streaming(response):
        def on_field(field):
            print(field)

        def on_file(file):
            print(file.in_memory, file.size, file.actual_file_name)
            indentifier = str(uuid.uuid4())
            storge_dir = os.path.join(storge_base, indentifier)
            if not os.path.isdir(storge_dir):
                os.makedirs(storge_dir, 0o777)
            # save the chunk data
            try:
                filename = file.file_name.decode()
                storge_file = os.path.join(storge_dir, filename)
                # extract starting byte from Content-Range header string
                with open(storge_file, 'wb') as f:
                    if file.in_memory:
                        f.write(file.file_object.getvalue())
                    else:
                        with open(file.actual_file_name, 'rb') as tmp_file:
                            f.write(tmp_file.read())
                    response.write(indentifier)

                metadata_file = os.path.join(storge_dir, 'metadata')
                with open(metadata_file, 'w') as f:
                    f.write(json.dumps({
                            'indentifier': indentifier,
                            'filename': filename,
                            }))
            except Exception as e:
                response.write('can not save file in to stroge' + str(e))

        callbacks = {
            'on_field': on_field,
            'on_file': on_file,
        }
        parser = create_form_parser(request.headers, **callbacks)
        while True:
            content = await request.stream.get()
            if content:
                parser.write(content)
            else:
                break
    return response.stream(streaming, content_type='application/json')


#below code didnot tested
@app.route("convert/resumable_upload", methods=['POST', 'GET'])
async def resumable_upload(request):
    temp_base = '/tmp'
    storge_base = StorgePath

    if request.method == "OPTION":

        resumableIdentfier = request.args.get('resumableIdentifier', None)
        resumableFilename = request.args.get('resumableFilename', None)
        resumableChunkNumber = request.args.get('resumableChunkNumber', None)

        if not resumableIdentfier or not resumableFilename or not resumableChunkNumber:
            # Parameters are missing or invalid
            raise ServerError('no chunk fileds')

        # chunk folder path based on the parameters
        temp_dir = os.path.join(temp_base, resumableIdentfier)

        # chunk path based on the parameters
        chunk_file = os.path.join(temp_dir, get_chunk_name(
            resumableFilename, resumableChunkNumber))

        if os.path.isfile(chunk_file):
            # Let resumable.js know this chunk already exists
            return response.text('ok')
        else:
            # Let resumable.js know this chunk does not exists and needs to be uploaded
            raise NotFound('no chunk')

    if request.method == "POST":
        resumableTotalChunks = request.form.get('resumableTotalChunks', None)
        resumableChunkNumber = request.form.get('resumableChunkNumber', None)
        resumableFilename = request.form.get('resumableFilename', None)
        resumableIdentfier = request.form.get('resumableIdentifier', None)

        # get the chunk data
        chunk_data = request.files['files[]']

        # make our temp directory
        temp_dir = os.path.join(temp_base, resumableIdentfier)
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir, 0o777)

        # save the chunk data
        chunk_name = get_chunk_name(resumableFilename, resumableChunkNumber)
        chunk_file = os.path.join(temp_dir, chunk_name)
        chunk_data.save(chunk_file)

        # check if the upload is complete
        chunk_paths = [os.path.join(temp_dir, get_chunk_name(resumableFilename, x)) for x in
                       range(1, resumableTotalChunks + 1)]
        upload_complete = all([os.path.exists(p) for p in chunk_paths])

        # combine all the chunks to create the final file
        if upload_complete:
            FILE_IDENTFIER = str(uuid.uuid4())
            target_file_name = os.path.join(storge_base, FILE_IDENTFIER)
            with open(target_file_name, "ab") as target_file:
                for p in chunk_paths:
                    stored_chunk_file_name = p
                    stored_chunk_file = open(stored_chunk_file_name, 'rb')
                    target_file.write(stored_chunk_file.read())
                    stored_chunk_file.close()
                    os.unlink(stored_chunk_file_name)
            target_file.close()
            os.rmdir(temp_dir)

        return response.text('ok')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8881)