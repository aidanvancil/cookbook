import requests
from decouple import config
from urllib.parse import quote


API_APP_ID = config('API_APP_ID')
API_APP_KEY = config('API_APP_KEY')

def get_recipes(query):
    api_url = f'https://api.edamam.com/api/recipes/v2?app_id={API_APP_ID}&app_key={API_APP_KEY}&q={query}&type=public'

    response = requests.get(api_url)
    
    if response.status_code == 200:
        return response.json().get('hits', [])
    else:
        return []

def get_recipe_by_url(recipe_url):
    encoded_recipe_url = quote(recipe_url)

    api_url = f'https://api.edamam.com/api/recipes/v2/by-uri?app_id={API_APP_ID}&app_key={API_APP_KEY}&uri={encoded_recipe_url}&type=public'
    response = requests.get(api_url)
    print(response.json())

    if response.status_code == 200:
        return response.json().get('hits', {})[0]
    else:
        return None