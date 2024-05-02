import streamlit as st
import requests
import json
from PIL import Image
import io

# Fetch ingredients from TheMealDB API
def fetch_ingredients():
    response = requests.get("https://www.themealdb.com/api/json/v1/1/list.php?i=list")
    data = response.json()
    ingredients = [item["strIngredient"] for item in data["meals"]]
    return ingredients

# Fetch all recipes and store them with their ingredients
def fetch_recipes():
    recipes = {}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        response = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?f={letter}")
        data = response.json()
        if data['meals'] is not None:
            for meal in data['meals']:
                recipes[meal['strMeal']] = {f"strIngredient{i}": meal.get(f"strIngredient{i}", "") for i in range(1, 21)}
    return recipes

# Function to find recipes based on selected ingredients
def find_recipes(selected_ingredients, recipes):
    matched_recipes = {}
    for recipe_name, ingredients in recipes.items():
        score = sum(1 for i in range(1, 21) if ingredients.get(f"strIngredient{i}", "") in selected_ingredients)
        if score > 0:
            matched_recipes[recipe_name] = score
    return matched_recipes

# Streamlit interface coponenet
st.title("Chichou's ingredient finder")
ingredients = fetch_ingredients()
selected_ingredients = st.multiselect('Select your ingredients:', ingredients)

if selected_ingredients:
    recipes = fetch_recipes()
    recommended_recipes = find_recipes(selected_ingredients, recipes)
    for recipe_name, score in recommended_recipes.items():
        if st.button(f"{recipe_name} (matches: {score})"):
            response = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={recipe_name}")
            recipe_details = response.json()['meals'][0]
            image_url = recipe_details['strMealThumb']
            st.image(image_url, caption=recipe_name, width=300)
            st.write(f"### Ingredients and Instructions for {recipe_name}")
            for i in range(1, 21):
                ingredient = recipe_details.get(f'strIngredient{i}', None)
                measure = recipe_details.get(f'strMeasure{i}', None)
                if ingredient and measure:
                    st.write(f"{ingredient}: {measure}")
            st.write("### Instructions")
            st.write(recipe_details['strInstructions'])
else:
    st.write("Please select some ingredients to find recipes.")
