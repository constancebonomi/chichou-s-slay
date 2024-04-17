#This code imports the .json file of all recipes from TheMealDB (#1), reformats it into a recipe list (#2),
# makes a list of recipe names (#3), and a dictionary with each recipe and its ingredients (#4).
# I recommend you run this code in an empty Jupyter notebook.
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


from PIL import Image
import urllib.request
import io

URL = reformatted_allrecipeslist[25]["strMealThumb"]


with urllib.request.urlopen(URL) as url:
    f = io.BytesIO(url.read())

    
img = Image.open (f)

img.show ()

import requests
import json

response_API = requests.get("https://www.themealdb.com/api/json/v1/1/list.php?i=list")

data =response_API.text
parse_json = json.loads(data)
new_variable = parse_json["meals"][9]["strIngredient"]

liste = []
for number in range(0,len(parse_json ["meals"])-1):
    ingredient = parse_json["meals"][number]["strIngredient"]
    liste.append (ingredient)
list.sort (liste)
print (liste)

print ("Which ingredients do you want to use?", new_variable)


