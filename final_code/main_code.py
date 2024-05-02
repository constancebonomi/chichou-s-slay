import streamlit as st
import requests as rq
import json
from PIL import Image
import urllib.request
import io

class Chosen_Meal:
    #we define a class Chosen_Meal that is destined to facilitate working with the results of the recipe_search function
    
    def __init__ (self, mealname): #three attributes: name, full recipe attributes dictionary, recipe full text
        self.mealname = str(mealname)
        self.fullrecipe = rq.get("https://www.themealdb.com/api/json/v1/1/search.php?s="+str(mealname)).json()["meals"][0]
        #the recipe attributes dictionary is imported live from the TheMealDB API
        self.recipetext = self.fullrecipe["strInstructions"]
        
        self.ingredientswithquantities = {}
        #dictionary of all recipe ingredients with their quantities
        for numbertotwenty in range(1, 21):
            self.ingredientswithquantities[self.fullrecipe["strIngredient"+str(numbertotwenty)]] = f'{str(self.fullrecipe["strMeasure"+str(numbertotwenty)])}'
        
        self.ingredients_text = ""
        #text form of the ingredients list
        for ingredient, quantity in self.ingredientswithquantities.items():
            if ingredient:
                self.ingredients_text += f'{ingredient}: {quantity}\n'
    
    def __str__ (self):
        #string representation shows text with recipe name, a formatted list of ingredients, and the recipe preparation text
        return f'''{self.mealname}:\n\n
    Ingredients:\n
    {self.ingredients_text}\n
    {self.recipetext}'''
    
    def photo(self):
        #object method to show a photo
        image_URL = self.fullrecipe["strMealThumb"]
        with urllib.request.urlopen(image_URL) as url:
            f = io.BytesIO(url.read())
        img = Image.open (f)
        return img.show ()



#importing ingredients directly from TheMealDB API
def fetch_ingredients():
    response = rq.get("https://www.themealdb.com/api/json/v1/1/list.php?i=list")
    data = response.json()
    ingredients = [item["strIngredient"] for item in data["meals"]]
    return ingredients

#importing saved reformatted database of recipes with ingredients
recipedict_withingredients = dict(rq.get("https://raw.githubusercontent.com/constancebonomi/chichou-s-slay/main/final_code/recipedict_withingredients.json").json())

def recipesearch (chosen_ingredients_list = [], recipedict_withingredients = {}):
    
    #This function takes a list of ingredients and returns the 5 recipes in the TheMealDB database
    #that contain the most of these ingredients
    
    #This part of the function defines a dictionary with each recipe name and 
    #its corresponding similarity score to the chosen ingredients list.
    
    recipedict_withscores = {}
    for recipename, recipe_ingredients_list in recipedict_withingredients.items():
        for recipe_ingredient in set(recipe_ingredients_list):
            #set because some TheMealDB recipes contain duplicate ingredients
            #The loop below creates a score field for a recipe if it's empty, and adds one if it exists
            if recipe_ingredient in chosen_ingredients_list:
                if recipedict_withscores.get(recipename) == None:
                       recipedict_withscores[recipename] = 1
                else: recipedict_withscores[recipename] += 1
                    
    #This part of the function defines a dictionary with the top five recipes and 
    #their corresponding similarity scores to the chosen ingredients list.                  
    
    recipes_result = {}
    recipe_results_length = 0
    for diminishing_similarity_coefficient in range(3):
        #this is a variable that will be substracted from len(chosen ingredients), so that the most fitting recipes appear first
        for recipestr, recipescore in recipedict_withscores.items():
            if recipe_results_length < 5:
                #the maximal number of recommendations is set to five.
                if recipescore == (len(chosen_ingredients_list) - diminishing_similarity_coefficient):
                        recipes_result[recipestr] = recipescore
                        recipe_results_length += 1
            
    return recipes_result

def recipresult_objects(resultsdictionary = {}):
    chosen_recipes_names_list = list(resultsdictionary.keys())
    recipe1 = Chosen_Meal(chosen_recipes_names_list[0])
    recipe2 = Chosen_Meal(chosen_recipes_names_list[1])
    recipe3 = Chosen_Meal(chosen_recipes_names_list[2])
    recipe4 = Chosen_Meal(chosen_recipes_names_list[3])
    recipe5 = Chosen_Meal(chosen_recipes_names_list[4])
    reciperesult_objects_list = [recipe1, recipe2, recipe3, recipe4, recipe5]
    return reciperesult_objects_list


# Streamlit interface component
st.title("Chichou's ingredient finder")
ingredients = fetch_ingredients()
selected_ingredients = list(st.multiselect('Select your ingredients:', ingredients))

if selected_ingredients:
    recipes = fetch_recipes()
    recommended_recipes = recipesearch(selected_ingredients, recipedict_withingredients)
    for recipe_name, score in recommended_recipes.items():
        if st.button(f"{recipe_name} (matches: {score})"):
            response = rq.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={recipe_name}")
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
