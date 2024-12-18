import streamlit as st
import requests
import os

API_KEY = os.getenv('SPOONACULAR_API_KEY')
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
    if instructions and instructions[0].get('steps'):
        for idx, step in enumerate(instructions[0]['steps'], start=1):
            steps.append(f"{idx}. {step['step']}")
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


st.set_page_config(
    page_title="MelonEats",
    page_icon="🍈",
    layout="wide"
)

# Streamlit Application
st.title("MelonEats - Recipe Finder")
st.markdown('''
            Welcome to my little project!
            
            This is a simple tool that you can use to get a random recipe by inputting any ingredients you have.
            If you're like me who just cook with whatever I have in my fridge, this will be helpful to you too!
            
            Thank you for trying it out, have fun~
            
            Notes: There's a daily limit of 150 requests. It's a free API, sorry xD
            ''')

# User Inputs
query = st.text_input(
    "Enter the ingredients that you have (e.g., chicken, chili, cheese, beef, pasta):")
number = st.number_input("Number of recipes to show:",
                         min_value=1, max_value=10, value=5)

if st.button("Fetch Recipes"):
    with st.spinner("Fetching recipes..."):
        data = fetch_recipes(query, API_KEY, number)
        if data and 'results' in data:
            recipes = process_recipes(data['results'])
            for recipe in recipes:
                with st.container(height=500):
                    col1, col2 = st.columns([4, 6])
                    with col1:
                        st.subheader(recipe['recipe_name'])
                        col3, col4 = st.columns([2, 2])
                        with col3:
                            if recipe['image']:
                                st.image(recipe['image'], width=300)
                            st.markdown(
                                f"**Source:** [Link]({recipe['recipe_source']})")
                            st.markdown(
                                f"**Cooking Time:** {recipe['cooking_time']} minutes")
                            st.markdown(f"**Servings:** {recipe['servings']}")
                        with col4:
                            st.markdown("**Ingredients:**")
                            st.text(recipe['ingredients'])
                    with col2:
                        st.subheader("How to make it:")
                        st.markdown("**Steps:**")
                        st.text(recipe['steps'])
        else:
            st.warning("No recipes found or API error occurred.")
