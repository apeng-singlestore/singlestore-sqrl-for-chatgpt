import json

import quart
import quart_cors
from quart import request
import requests


app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


# Keep track of username and password
username = 'admin'
password = 'Password!'

# Add the new API endpoint
@app.post("/sql_query")
async def execute_sql_query():
    request_data = await quart.request.get_json(force=True)
    sql_query = request_data["sql_query"]
    result = post_sql_query(sql_query, "s2_dataset_trades_fb76a929", username, password)
    return quart.Response(response=json.dumps(result), status=200)

def post_sql_query(sql_query, db_name, username, password):
    url = "https://svc-e846ab48-fb29-4054-97c1-751a295fb357-dml.aws-oregon-4.svc.singlestore.com/api/v2/query/rows"
    
    # Add the authorization header
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {"sql": sql_query, "database": db_name}

    
    response = requests.post(url, headers=headers, data=json.dumps(data), auth=(username, password))
    print(response)
    return response.json()

    
@app.get("/table_shape")
async def get_table_shape():
    query = "select table_name, column_name from information_schema.columns where table_schema != \"information_schema\""
    result = post_sql_query(query, "information_schema", username, password)
    return quart.Response(response=json.dumps(result), status=200)




@app.post("/todos/<string:username>")
async def add_todo(username):
    request = await quart.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request["todo"])
    return quart.Response(response='OK', status=200)

@app.get("/todos/<string:username>")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)

@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request = await quart.request.get_json(force=True)
    todo_idx = request["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response='OK', status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
