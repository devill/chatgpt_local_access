import json
import os
from quart import Quart, request, Response, send_file
from quart_cors import cors

app = cors(Quart(__name__), allow_origin="https://chat.openai.com")

@app.get("/listDir")
async def list_dir():
    path = request.args.get('path')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    order = request.args.get('order', 'name')
    direction = request.args.get('direction', 'asc')

    if limit > 100:
        return Response("Error: Page size limit exceeded. Maximum 100 entries per page.", status=400)

    try:
        files = os.listdir(path)
        file_info_list = []
        for file in files:
            file_info = os.stat(os.path.join(path, file))
            file_info_list.append({
                'name': file,
                'size': file_info.st_size,
                'modified': file_info.st_mtime
            })

        file_info_list.sort(key=lambda x: x[order], reverse=(direction == 'desc'))

        start = (page - 1) * limit
        end = start + limit
        return Response(json.dumps(file_info_list[start:end]), mimetype='application/json')
    except Exception as e:
        return Response(str(e), status=400)

@app.get("/getFileInfo")
async def get_file_info():
    path = request.args.get('path')
    try:
        file_info = os.stat(path)
        return Response(json.dumps({
            'size': file_info.st_size,
            'modified': file_info.st_mtime
        }), mimetype='application/json')
    except Exception as e:
        return Response(str(e), status=400)

@app.get("/getFileContent")
async def get_file_content():
    path = request.args.get('path')
    offset = int(request.args.get('offset', 0))

    try:
        with open(path, 'r') as f:
            f.seek(offset)
            content = f.read(5000)
            return Response(json.dumps({
                'content': content
            }), mimetype='application/json')
    except Exception as e:
        return Response(str(e), status=400)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return Response(text, mimetype="application/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

def main():
    port = int(os.environ.get("PORT", 5004))
    app.run(debug=True, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
