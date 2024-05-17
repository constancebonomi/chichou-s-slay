import streamlit as st
import requests as rq
import json
from PIL import Image
import urllib.request
import io
import matplotlib.pyplot as plt

#This code has 6 parts.
#1. The class Chosen_Meal is defined to facilitate working with the chosen recipe down the road
#2. The list of all ingredients is imported from the TheMealDB API directly (live API connection)
#3. A reformatted version of the TheMealDB recipes database is imported from our own json document saved on github, https://raw.githubusercontent.com/constancebonomi/chichou-s-slay/main/final_code/recipedict_withingredients.json
        #3b. The reformatting code is saved under https://raw.githubusercontent.com/constancebonomi/chichou-s-slay/main/final_code/loading_data.json
#4. We define a function matching a list of chosen ingredients from the TheMealDB ingredients list to max 5 recipes from the TheMealDB database.
#5. We program the streamlit interface 
#6. We add a matplotlib vertical bar chart that shows the amount of calories in each ingredient of the chosen recipe.
    #6b. The calories per 100g of an ingredient, and conversion rates (e.g. tbsp to units of 100g) were generated on ChatGPT.
    #6c. The reformatted table is available under https://raw.githubusercontent.com/constancebonomi/chichou-s-slay/main/final_code/recipedict_withkcal.json
    #6d. Our code for converting the ChatGPT output is available under https://raw.githubusercontent.com/constancebonomi/chichou-s-slay/main/final_code/loading_recipe_kcal_data.json

#1. (Constance)
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
        image_url = self.fullrecipe["strMealThumb"]
        return image_url


#2. (Alex)
#importing ingredients directly from TheMealDB API
def fetch_ingredients():
    response = rq.get("https://www.themealdb.com/api/json/v1/1/list.php?i=list")
    data = response.json()
    ingredients = [item["strIngredient"] for item in data["meals"]]
    return ingredients
    
#3. (Jeremi)
#importing saved reformatted database of recipes with ingredients
recipedict_withingredients = dict(rq.get("https://raw.githubusercontent.com/constancebonomi/chichou-s-slay/main/final_code/recipedict_withingredients.json").json())

#4. (Jeremi)
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



#5. Streamlit interface component (Esteban)
st.title("MealCraft")
ingredients = fetch_ingredients()
selected_ingredients = list(st.multiselect('Select your ingredients:', ingredients)) #multiselect list with search bar

if selected_ingredients:
    recipes = recipedict_withingredients
    recommended_recipes = recipesearch(selected_ingredients, recipedict_withingredients)
    for recipe_name, score in recommended_recipes.items():
        if st.button(f"{recipe_name} (matches: {score})"):
            chosen_meal = Chosen_Meal(str(recipe_name))
            st.image(chosen_meal.photo(), caption=recipe_name, width=300)
            st.write(f"### Ingredients and Instructions for {recipe_name}")
            st.write(chosen_meal)
            st.write("Calorie overview:")
            
#6. (Sofia)
#We define a matplotlib plot that, for the chosen recipe, shows the calories of each ingredients and the sum total of recipe calories
            fig,ax = plt.subplots(1)
            recipe_name = str(recipe_name)
            ingredients = rq.get('https://raw.githubusercontent.com/constancebonomi/chichou-s-slay/main/final_code/recipedict_withkcal.json').json()[recipe_name]
            sum_kcal = 0
            idx = 0
            idx_name_list = []
            for i in range(20):
                ingredient = ingredients[f"ingredient_{i}"]
            
            
                kcal = ingredient["calories_100g"]
                amount = ingredient["amount"]
            
                if kcal == None or amount == None:
                    continue #continue so that loop does not break up when an ingredient does not exist or have calories (e.g. water)
                kcal = amount*kcal/100.0
            
                sum_kcal += kcal
            
                ax.bar(idx, kcal, color = "green") #green bar chart showing the calories for each ingredient number
                idx_name_list.append(f"{ingredient['name']}\n{amount}g")
                idx += 1
            
            idx_sum = idx+2
            
            
            ax.bar(idx_sum, sum_kcal)
            ax.set_xticks(list(range(len(idx_name_list)))+[idx_sum],idx_name_list+["Total calories"], fontsize=10, rotation=45)
            ax.set_xlabel('Ingredients', fontsize=12) #axis labels
            ax.set_ylabel('Calories (kcal)', fontsize=12) #axis labels
            ax.set_title(f"Recipe: {recipe_name}", fontsize=15) #title
            ax.grid()
            fig.tight_layout()
            
            st.write(fig) #command to make streamlit show the figure defined above
else:
    st.write("Please select some ingredients to find recipes.")
