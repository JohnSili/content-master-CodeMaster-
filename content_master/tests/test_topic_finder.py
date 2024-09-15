import requests

url = "https://linkedin-data-api.p.rapidapi.com/get-company-by-domain"

querystring = {"domain":"apple.com"}

headers = {
	"x-rapidapi-key": "094c59a3e9msha54e7ff64c6d6dcp125441jsnf4e2b18672c4",
	"x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())