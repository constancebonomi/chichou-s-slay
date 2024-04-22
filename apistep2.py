#This code imports the .json file of all recipes from TheMealDB (#1), reformats it into a recipe list (#2),
# makes a list of recipe names (#3), and a dictionary with each recipe and its ingredients (#4).
# You can print the intermediate results at each step to see what it does.

import requests as rq #library for accessing APIs
import string as alphabet #library generating strings

#1
allrecipesdictionary = {}
for letter in list(alphabet.ascii_lowercase): #for loop for each letter in the alphabet
    letterresult = rq.get(f"https://www.themealdb.com/api/json/v1/1/search.php?f={letter}").json()
    #normal http request function that imports a json file with all recipes starting with a given letter, for all letters
    #TheMealDB is structured per letter, so we need to repeat this request 26 times in a for loop.
    allrecipesdictionary[letter] = letterresult
    #this function, repeated in the for loop, joins all results in a single dictionary, allrecipesdictionary.

#print(allrecipesdictionary['a']['meals'])
#As you can see if you print, this dictionary is still complex.


#2
reformatted_allrecipeslist = []    
for letter in list(alphabet.ascii_lowercase):
    if allrecipesdictionary[letter]['meals']:
    #this is a quick if function that excludes empty items. We have no recipes starting with x, for example.
        all_recipes_letter = allrecipesdictionary[letter]['meals']
        reformatted_allrecipeslist += all_recipes_letter

#This reformatted_allrecipeslist is a list with each of its items being a dictionary containing all info on a given recipe.
#print(reformatted_allrecipeslist)

recipenamelist = []
for recipeindex in range(len(reformatted_allrecipeslist)-1):
    recipenamelist.append(str(reformatted_allrecipeslist[recipeindex]['strMeal']))

#This is a list of fhe names of all the recipes we have at our disposal. Maybe it will be useful.
#print(recipenamelist)

recipedict_withingredients = {}
for recipedescription in reformatted_allrecipeslist:
    recipeingredients = []
    for number in range(1,20): #in the API, a recipe has a maximum of 20 ingredients. They are stored in 20 values.
        ingredientnumber = "strIngredient" + f'{number}'
        recipeingredients.append(recipedescription[ingredientnumber])
    recipedict_withingredients[recipedescription['strMeal']] = recipeingredients

#This is a dictionary of all recipes with their respective ingredients. You can print it below.
#for recipename in recipedict_withingredients:
    #print(f'{recipename}: {recipedict_withingredients[recipename]}\n')



def recipesearch (chosen_ingredients_list = [], recipedict_withingredients = {}):
    
    #This function takes a list of ingredients and returns the 5 recipes in the TheMealDB database
    #that contain the most of these ingredients
    
    #This part of the function defines a dictionary with each recipe name and 
    #its corresponding similarity score to the chosen ingredients list.
    
    recipedict_withscores = {}
    for recipename, recipe_ingredients_list in recipedict_withingredients.items():
        for recipe_ingredient in set(recipe_ingredients_list):
            #set because some TheMealDB recipes contain duplicate ingredients
            if recipe_ingredient in chosen_ingredients_list:
                if recipedict_withscores.get(recipename) == None:
                       recipedict_withscores[recipename] = 1
                else: recipedict_withscores[recipename] += 1
                    
    #This part of the function defines a dictionary with the top five recipes and 
    #their corresponding similarity scores to the chosen ingredients list.                  
    
    recipes_result = {}
    recipe_results_length = 0
    for diminishing_similarity_coefficient in range(3):
        for recipestr, recipescore in recipedict_withscores.items():
            if recipe_results_length < 5:
                if recipescore == (len(chosen_ingredients_list) - diminishing_similarity_coefficient):
                        recipes_result[recipestr] = recipescore
                        recipe_results_length += 1
            
    return recipes_result


ingredientslist = ["Veal", "Basil Leaves", "Carrot"]
chosen_recipeslist = list(recipesearch(ingredientslist, recipedict_withingredients).keys())

from PIL import Image
import urllib.request
import io

class Chosen_Meal:
    
    def __init__ (self, mealname):
        self.mealname = str(mealname)
        self.fullrecipe = rq.get("https://www.themealdb.com/api/json/v1/1/search.php?s="+str(mealname)).json()["meals"][0]
        self.recipetext = self.fullrecipe["strInstructions"]
        
        self.ingredientswithquantities = {}
        for numbertotwenty in range(1, 21):
            self.ingredientswithquantities[self.fullrecipe["strIngredient"+str(numbertotwenty)]] = f'{str(self.fullrecipe["strMeasure"+str(numbertotwenty)])}'
        
        self.ingredients_text = ""
        for ingredient, quantity in self.ingredientswithquantities.items():
            if ingredient:
                self.ingredients_text += f'{ingredient}: {quantity}\n'
               

    
    def __str__ (self):
        return f'''{self.mealname}:\n\n
    Ingredients:\n
    {self.ingredients_text}\n
    {self.recipetext}'''
    
    def photo(self):
        image_URL = self.fullrecipe["strMealThumb"]
        with urllib.request.urlopen(image_URL) as url:
            f = io.BytesIO(url.read())
        img = Image.open (f)
        return img.show ()
    
recipeobjectslist = []
for localindex in range(4):
    recipeobjectslist.append(Chosen_Meal(chosen_recipeslist[localindex]))
for recipeobject in recipeobjectslist: 
    print(recipeobject)
    recipeobject.photo()