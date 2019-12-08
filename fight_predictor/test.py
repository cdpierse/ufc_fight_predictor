import requests

url = "http://localhost:5000/fight-predictor/api/v1.0/predict"

querystring = {"fighter1":"Henry Cejudo","fighter2":"Joe Lauzon"}

payload = ""

response = requests.request("GET", url, params=querystring)

print(response.text)