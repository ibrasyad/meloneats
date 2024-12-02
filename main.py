import requests
import json
import os

API_KEY = os.getenv('SPOONACULAR_API_KEY')
API_ENDPOINT = "https://api.spoonacular.com/recipes/complexSearch"

if not API_KEY:
    print("Error: API Key is missing. Set it as an environment variable.")
    exit()


def fetch_recipes(query, api_key, number=5):
    """Fetches recipes matching a query."""
    params = {
        "query": query,
        "apiKey": api_key,
        "number": number,
        "ignorePantry": True,
        "addRecipeInformation": True,
        "addRecipeInstructions": True,
        "addRecipeNutrition": True,
    }
    response = requests.get(API_ENDPOINT, params=params)
    if response.status_code == 200:
        return response.json()
    print(f"Error: {response.status_code} - {response.text}")
    return None


def parse_ingredients(ingredients_list):
    """Parses and formats ingredients from API response."""
    ingredients = []
    for ingredient in ingredients_list:
        unit = f" {ingredient['unit']}" if ingredient['unit'] else ''
        ingredients.append(
            f"{ingredient['amount']}{unit} of {ingredient['name']}")
    return "\n".join(ingredients)


def parse_steps(instructions):
    """Parses and formats steps from API response."""
    steps = []
    if instructions and instructions[0]['steps']:
        for step in instructions[0]['steps']:
            steps.append(step['step'])
    return "\n".join(steps)


def fetch_paginated_recipes(query, api_key, total=10):
    """Fetches paginated results for larger datasets."""
    recipes = []
    while len(recipes) < total:
        params = {
            "query": query,
            "apiKey": api_key,
            "offset": len(recipes),
            "number": min(total - len(recipes), 5),
            "ignorePantry": True,
            "addRecipeInformation": True,
            "addRecipeInstructions": True,
            "addRecipeNutrition": True,
        }
        response = requests.get(API_ENDPOINT, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'results' not in data:
                break
            recipes.extend(data['results'])
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    return recipes[:total]


def process_recipes(data):
    """Processes raw API response into structured recipes."""
    result = []
    for i in data:
        recipe = {
            'recipe_name': i.get('title', 'Unknown Recipe'),
            'recipe_source': i.get('sourceUrl', 'No source available'),
            'cooking_time': i.get('readyInMinutes', 'Unknown'),
            'servings': i.get('servings', 'Unknown'),
            'image': i.get('image', ''),
            'summary': i.get('summary', 'No summary available'),
            'ingredients': '',
            'step': ''
        }
        recipe['ingredients'] = parse_ingredients(
            i['nutrition']['ingredients']) if 'nutrition' in i else "No ingredients available."
        recipe['step'] = parse_steps(i['analyzedInstructions'])
        result.append(recipe)
    return result


def display_recipes(recipes):
    """Prints recipe details in a user-friendly format."""
    for recipe in recipes:
        print(f"Recipe Name: {recipe['recipe_name']}")
        print(f"Source: {recipe['recipe_source']}")
        print(f"Cooking Time: {recipe['cooking_time']} minutes")
        print(f"Servings: {recipe['servings']}")
        print(f"Ingredients:\n{recipe['ingredients']}")
        print(f"Steps:\n{recipe['step']}")
        print("-" * 40)


if __name__ == "__main__":
    recipe_query = input("Enter a recipe query (e.g., chicken): ").strip()
    total_recipes = int(input("How many recipes do you want to fetch? "))
    data = fetch_paginated_recipes(recipe_query, API_KEY, total_recipes)

    if not data:
        print("No recipes found or API error occurred.")
        exit()

    recipes = process_recipes(data)
    display_recipes(recipes)
