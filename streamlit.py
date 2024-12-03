import streamlit as st
import requests

# Constants
API_KEY = "b08057471dc3450cbe373a2f074efb7d"
API_ENDPOINT = "https://api.spoonacular.com/recipes/complexSearch"


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
    st.error(f"Error: {response.status_code} - {response.text}")
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
            'steps': ''
        }
        recipe['ingredients'] = parse_ingredients(
            i['nutrition']['ingredients']) if 'nutrition' in i else "No ingredients available."
        recipe['steps'] = parse_steps(i['analyzedInstructions'])
        result.append(recipe)
    return result


# Streamlit Application
st.title("Recipe Finder")

# User Inputs
query = st.text_input("Enter a recipe query (e.g., chicken, pasta):")
number = st.number_input("Number of recipes to fetch:",
                         min_value=1, max_value=20, value=5)

if st.button("Fetch Recipes"):
    with st.spinner("Fetching recipes..."):
        data = fetch_recipes(query, API_KEY, number)
        if data and 'results' in data:
            recipes = process_recipes(data['results'])
            for recipe in recipes:
                st.subheader(recipe['recipe_name'])
                if recipe['image']:
                    st.image(recipe['image'], width=300)
                st.markdown(f"**Source:** [Link]({recipe['recipe_source']})")
                st.markdown(
                    f"**Cooking Time:** {recipe['cooking_time']} minutes")
                st.markdown(f"**Servings:** {recipe['servings']}")
                st.markdown("**Ingredients:**")
                st.text(recipe['ingredients'])
                st.markdown("**Steps:**")
                st.text(recipe['steps'])
                st.markdown("---")
        else:
            st.warning("No recipes found or API error occurred.")
