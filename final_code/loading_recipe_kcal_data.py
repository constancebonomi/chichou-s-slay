

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
    calorieslistimport = str(rq.get("https://raw.githubusercontent.com/constancebonomi/chichou-s-slay/main/usecase_example/data_recipes/strIngredient_kcal100g.txt").content.decode("utf-8"))
    calorieslistimport = calorieslistimport.replace("kcal", "")
    
    # Splitting the import into lines
    lines = calorieslistimport.split("\n")

    #Putting it into the dictionary
    for line in lines:
        if line:
            ingredientname, calories = line.split(": ")
            map_strIngredient_2_kcal100g[ingredientname] = calories

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