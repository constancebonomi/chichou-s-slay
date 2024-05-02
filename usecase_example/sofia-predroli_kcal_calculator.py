import requests as rq 

import string as alphabet 
alphabet_letter_list = list(alphabet.ascii_lowercase)

import json 
import os 

#the function below imports all recipes from TheMealDB API and saves them in their own files via json.dump at their given address in the github repository.
def download_recipes():
    for letter in alphabet_letter_list: 
        json_recipes = rq.get(f"https://www.themealdb.com/api/json/v1/1/search.php?f={letter}").json()

        with open(os.path.join("data_recipes", f"{letter}.json"), "w") as f:
            json.dump(json_recipes, f)

#We previously ChatGPT-generated a list of calorie amounts per 100g serving for each of the ingredients in TheMealDB API.
#get_recipes cleans up this list, joins it with our existing TheMealDB ingredients list,
#and converts the quantities provided by TheMealDB (example: table spoon) to multiples of 100g
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

   #We generated a ChatGPT conversion list between quantities like "tablespoon" and units of 100g
    #This part cleans up the ChatGPT-generated calorie list and puts it into the map_strMeasure_strIngredient_2_weight dictionary
    map_strMeasure_strIngredient_2_weight = {}
    with open(os.path.join("data_recipes", "strMeasure_strIngredient_weight.txt"), 'r') as f:
        lines = f.readlines()

        for line in lines:
            parts = line.split(':')
            measure, ingredient, weight_in_gram = [part.strip() for part in parts]
            map_strMeasure_strIngredient_2_weight[(ingredient.lower(), measure.lower())] = weight_in_gram.replace("g", "")
 
 
    for letter in alphabet_letter_list:
        json_filename = os.path.join("data_recipes", "recipes_alphabetical_order", f"{letter}.json")

        json_data = None
        with open(json_filename, 'r') as f:
            json_data = json.load(f)
        
        if json_data and json_data["meals"]:
            for recipe in json_data["meals"]:
                ingredient_dict = {}
                for n in range(20):
                    ingredient_name   = recipe[f"strIngredient{n+1}"]
                    ingredient_amount = recipe[f"strMeasure{n+1}"]
                    
                    if (ingredient_name!="" and ingredient_amount!="") and (ingredient_name!=None and ingredient_amount!=None):
                        ingredient_amount = ingredient_amount.lower()
                        ingredient_name = ingredient_name.lower()

                        if (ingredient_name, ingredient_amount) in map_strMeasure_strIngredient_2_weight and \
                            ingredient_name in map_strIngredient_2_kcal100g:
                            
                            amount = map_strMeasure_strIngredient_2_weight[(ingredient_name, ingredient_amount)]
                            kcal   = map_strIngredient_2_kcal100g[ingredient_name]
                            
                            try:
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
                           
                output_data[recipe["strMeal"]] = ingredient_dict        

    return output_data


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig,ax = plt.subplots(1)
    #download_recipes()

    data = get_recipes()
        
    recipe_name = "Fish pie"

    ingredients = data[recipe_name]

    sum_kcal = 0
    idx = 0
    idx_name_list = []
    for i in range(20):
        ingredient = ingredients[f"ingredient_{i}"]


        kcal = ingredient["calories_100g"]
        amount = ingredient["amount"]

        if kcal == None or amount == None:
            continue
        kcal = amount*kcal/100.0
        
        sum_kcal += kcal

        ax.bar(idx, kcal, color = "green")
        idx_name_list.append(f"{ingredient['name']}\n{amount}g")
        idx += 1

    idx_sum = idx+2

    
    ax.bar(idx_sum, sum_kcal)
    ax.set_xticks(list(range(len(idx_name_list)))+[idx_sum],idx_name_list+["Total calories"], fontsize=10, rotation=45)
    ax.set_xlabel('Ingredients', fontsize=12)
    ax.set_ylabel('Calories (kcal)', fontsize=12)
    ax.set_title(f"Recipe: {recipe_name}", fontsize=15)
    ax.grid()
    fig.tight_layout()

    plt.show()
    
    
