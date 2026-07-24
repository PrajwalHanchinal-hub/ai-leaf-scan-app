import requests

url = "http://127.0.0.1:5000/upload"

file = {
    "image": open("test_leaf.jpg", "rb")
}

response = requests.post(url, files=file)

print(response.json())