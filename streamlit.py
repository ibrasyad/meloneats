import streamlit as st
import requests
import os
import time

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
            
            Notes: There should be delay of 20 seconds each use, I had to do it since I'm using a free API.
            ''')

# User Inputs
query = st.text_input(
    "Enter the ingredients that you have (e.g., chicken, chili, cheese, beef, pasta):")
number = st.number_input("Number of recipes to show:",
                         min_value=1, max_value=10, value=5)


# Initialize session state
if "fetch_button_disabled" not in st.session_state:
    st.session_state.fetch_button_disabled = False
if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = 0

# Disable the button for 30 seconds after clicking
if st.session_state.fetch_button_disabled:
    elapsed_time = time.time() - st.session_state.last_fetch_time
    if elapsed_time > 30:
        st.session_state.fetch_button_disabled = False
    else:
        st.info(
            f'''Please wait {30 - int(elapsed_time)}
                                      seconds to fetch recipes again.'''
        )


# Define the button and functionality
if st.button("Fetch Recipes", disabled=st.session_state.fetch_button_disabled):
    st.session_state.fetch_button_disabled = True
    st.session_state.last_fetch_time = time.time()

    with st.spinner("Fetching recipes..."):
        try:
            data = fetch_recipes(query, API_KEY, number)
            if data and 'results' in data:
                recipes = process_recipes(data['results'])
                for recipe in recipes:
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            if recipe.get('image'):
                                st.image(recipe['image'], width=150)
                            st.markdown(
                                f"**Source:** [Link]({recipe.get('recipe_source', 'N/A')})"
                            )
                            st.markdown(
                                f"**Cooking Time:** {recipe.get(
                                    'cooking_time', 'N/A')} minutes"
                            )
                            st.markdown(
                                f"**Servings:** {recipe.get('servings', 'N/A')}")
                        with col2:
                            st.subheader(recipe.get('recipe_name', 'Recipe'))
                            st.markdown("**Ingredients:**")
                            st.text("\n".join(recipe.get('ingredients', [])))
                            st.markdown("**Steps:**")
                            st.text("\n".join(recipe.get('steps', [])))
            else:
                st.warning("No recipes found or API error occurred.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
