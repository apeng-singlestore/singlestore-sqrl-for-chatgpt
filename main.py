import json
import quart
import quart_cors
from quart import request
import requests
import dotenv
import os

    
if not dotenv.load_dotenv():
    with open('.env', 'w') as f:
        f.write('USERNAME=\n')
        f.write('PASSWORD=\n')
        f.write('ENDPOINT_URL=\n')

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")
# Add the new API endpoint
@app.post("/sql_query")
async def execute_sql_query():
    request_data = await quart.request.get_json(force=True)
    sql_query = request_data["sql_query"]
    db_name = request_data["db_name"]
    result = post_sql_query(sql_query, db_name, os.getenv('USERNAME'), os.getenv('PASSWORD'))
    return quart.Response(response=json.dumps(result), status=200)

def post_sql_query(sql_query, db_name, username, password):
    print("CREDENTIALS")
    print(username)
    print(password)

    try:
        url = "https://" + os.getenv('ENDPOINT_URL') + "/api/v2/query/rows"
        
        # Add the authorization header
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {"sql": sql_query, "database": db_name}

        
        response = requests.post(url, headers=headers, data=json.dumps(data), auth=(username, password))
        print(response)
        return response.json()
    except:
        return quart.Response(response="SQL Query error. Please check your credentials.", status=400)

    
@app.get("/table_shape")
async def get_table_shape():
    query = "SELECT table_schema, table_name, GROUP_CONCAT(column_name SEPARATOR ', ') AS columns FROM information_schema.columns WHERE table_schema != 'information_schema' GROUP BY table_schema, table_name ORDER BY table_schema;"
    try:
        result = post_sql_query(query, "information_schema", os.getenv('USERNAME'), os.getenv('PASSWORD'))
        return quart.Response(response=json.dumps(result), status=200)
    except:
        return quart.Response(response="SQL Query error. Please check your credentials.", status=400)

        
    


@app.post("/credentials")
async def save_credentials():
    request_data = await quart.request.get_json(force=True)
    dotenv.set_key(dotenv_path=dotenv.find_dotenv(), key_to_set='USERNAME', value_to_set=request_data['username'])
    dotenv.set_key(dotenv_path=dotenv.find_dotenv(), key_to_set='PASSWORD', value_to_set=request_data['password'])
    dotenv.set_key(dotenv_path=dotenv.find_dotenv(), key_to_set='ENDPOINT_URL', value_to_set=request_data['endpoint_url'])
    dotenv.load_dotenv(override=True)
    return quart.Response(response="OK", status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo_main.png'
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
