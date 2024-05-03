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
        image_url = self.fullrecipe["strMealThumb"]
        return image_url



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


#We previously ChatGPT-generated a list of calorie amounts per 100g serving for each of the ingredients in TheMealDB API.
#get_recipes cleans up this list, joins it with our existing TheMealDB ingredients list,
#and converts the quantities provided by TheMealDB (example: table spoon) to grammes
def get_recipes():
    output_data = {}
    '''
    The output_data variable output_data is structured as follows:

    output_data = {
                        "recipe_0": { "ingredient_0" : {"amount": amount_0,  "calories_100g": calories_0, "nam  },   
                                      "ingredient_1" : {"amount": amount_1,  "calories_100g": calories_1  },
                                      ...,

                                      "ingredient_20": {"amount": amount_20, "calories_100g": calories_20 }   
                                    },

                        "recipe_1": { "ingredient_0" : {"amount": amount_0,  "calories_100g": calories_0  },
                                      "ingredient_1" : {"amount": amount_1,  "calories_100g": calories_1  },
                                      ...,

                                      "ingredient_20": {"amount": amount_20, "calories_100g": calories_20 }   
                                    },
                        ...,

                        "recipe_N": { "ingredient_0" : {"amount": amount_0,  "calories_100g": calories_0  },
                                      "ingredient_1" : {"amount": amount_1,  "calories_100g": calories_1  },
                                      ...,

                                      "ingredient_20": {"amount": amount_20, "calories_100g": calories_20 }   
                                    },

                  }                   
    '''
    #This part cleans up the ChatGPT-generated calorie list and puts it into the map_strIngredient_2_kcal100g dictionary
    map_strIngredient_2_kcal100g = {}
    with open(os.path.join("data_recipes", "strIngredient_kcal100g.txt"), 'r') as f:
        lines = f.readlines()

        for line in lines:
            parts = line.split(':')
            ingredient = parts[0].strip()
            kcal  = parts[1].strip().replace("kcal", "")
            map_strIngredient_2_kcal100g[ingredient.lower()] = kcal

   #We generated a ChatGPT conversion list between quantities like "tablespoon" and grammes
    #This part cleans up the ChatGPT-generated calorie list and puts it into the map_strMeasure_strIngredient_2_weight dictionary
    map_strMeasure_strIngredient_2_weight = {}
    with open(os.path.join("data_recipes", "strMeasure_strIngredient_weight.txt"), 'r') as f:
        lines = f.readlines()

        for line in lines:
            parts = line.split(':')
            measure, ingredient, weight_in_gram = [part.strip() for part in parts]
            map_strMeasure_strIngredient_2_weight[(ingredient.lower(), measure.lower())] = weight_in_gram.replace("g", "")
 
 #The below for loop joins the two dictionaries together and fills the new dictionary called output_data
    #with calorie amounts per 100g, in the format described in the ''' descriptive string ''' above.
    for letter in alphabet_letter_list:
        json_filename = os.path.join("data_recipes", "recipes_alphabetical_order", f"{letter}.json")

        #we open the recipe documentation for all recipes for each letter, from the github repository we previously saved.
        json_data = None
        with open(json_filename, 'r') as f:
            json_data = json.load(f)
            
        #we create a dictionary with, for each recipe, its ingredients and its amounts.        
        if json_data and json_data["meals"]:
            for recipe in json_data["meals"]:
                ingredient_dict = {}
                for n in range(20):
                    ingredient_name   = recipe[f"strIngredient{n+1}"]
                    ingredient_amount = recipe[f"strMeasure{n+1}"]

                    #This part is an if-loop that adds gram amounts and calorie amounts to the ingredient dictionary of a given recipe,
                    #but only if all this data is given and not null
                    if (ingredient_name!="" and ingredient_amount!="") and (ingredient_name!=None and ingredient_amount!=None):
                        ingredient_amount = ingredient_amount.lower()
                        ingredient_name = ingredient_name.lower()

                        if (ingredient_name, ingredient_amount) in map_strMeasure_strIngredient_2_weight and \
                            ingredient_name in map_strIngredient_2_kcal100g:
                            
                            amount = map_strMeasure_strIngredient_2_weight[(ingredient_name, ingredient_amount)]
                            kcal   = map_strIngredient_2_kcal100g[ingredient_name]
                            
                            try: #try-except implemented to avoid errors breaking the code
                                ingredient_dict[f"ingredient_{n}"] = { "amount"        : float(amount), 
                                                                       "calories_100g" : float(kcal),
                                                                       "name"          : ingredient_name }
                            except:
                                ingredient_dict[f"ingredient_{n}"] = { "amount"        : None, 
                                                                       "calories_100g" : None }
                        else:
                            ingredient_dict[f"ingredient_{n}"] = { "amount"        : None, 
                                                                   "calories_100g" : None }

                    else:
                        ingredient_dict[f"ingredient_{n}"] = { "amount"        : None, 
                                                               "calories_100g" : None }


                #finally, the ingredient weights and calorie amounts for each recipe are joined into a larger dict with all recipes
                output_data[recipe["strMeal"]] = ingredient_dict        

    return output_data


# Streamlit interface component
st.title("Chichou's ingredient finder")
ingredients = fetch_ingredients()
selected_ingredients = list(st.multiselect('Select your ingredients:', ingredients))

if selected_ingredients:
    recipes = recipedict_withingredients
    recommended_recipes = recipesearch(selected_ingredients, recipedict_withingredients)
    for recipe_name, score in recommended_recipes.items():
        if st.button(f"{recipe_name} (matches: {score})"):
            chosen_meal = Chosen_Meal(str(recipe_name))
            st.image(chosen_meal.photo(), caption=recipe_name, width=300)
            st.write(f"### Ingredients and Instructions for {recipe_name}")
            st.write(chosen_meal)
            if st.button("Check calories!"):
                st.write("The column chart for calories is in development")
else:
    st.write("Please select some ingredients to find recipes.")
