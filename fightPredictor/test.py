import requests

url = "http://localhost:5000/fight-predictor/api/v1.0/predict"

payload = "{\n    \"data\": {\n        \"fighter1\": \"Joe Lauzon\",\n        \"fighter2\": \"Henry Cejudo\"\n    }\n}"
#data = {"data": {"fighter1":"Joe Lauzon", "fighter2": "Henry Cejudo"}}
headers = {
    'Content-Type': "application/json",
    'User-Agent': "PostmanRuntime/7.20.1",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "3640fe30-07e1-4817-b9d7-176926b1b19a,0db4e099-7643-4d4b-accb-d612e73e0d4b",
    'Host': "localhost:5000",
    'Accept-Encoding': "gzip, deflate",
    'Content-Length': "78",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.get(url, data = payload, headers = {})

print(response.text)