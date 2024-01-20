import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import csv

class RecipeScrapper:
    def __init__(self,keyword):
        self.keyword = keyword
        self.recipes = {}
        
    def get_urls(self):
        url = f"https://www.myrecipes.com/search?q={self.keyword}"
        r = requests.get(url)
        
        soup = BeautifulSoup(r.text, 'html.parser')
        mydivs = soup.find_all("div", {"class": "searchResult__content"})
        recipes = {}
        for div in mydivs:
            self.recipes[div.span.text] = {'recipe_link': div.a['href']}

    def get_data(self):
        self.get_urls()
        
        for key, value in self.recipes.items():
            print(key, value['recipe_link'])
            r = requests.get(value['recipe_link'])
            soup = BeautifulSoup(r.text, 'html.parser')
            #Get Ingredients
            ingredients = soup.find_all("ul", {"class": "ingredients-section"})
            if ingredients != []:
                ingredients_list = [li.text.strip() for li in ingredients[0].find_all("li")]
                value['ingredients'] = ingredients_list
            else:
                value['ingredients'] = None
            #Get Metadata
            recipe_metadata = soup.find_all("div", {"class": "recipe-meta-item"})
            if recipe_metadata != []:
                recipe_metadata_values = {}
                for data in recipe_metadata:
                    metadata_text = data.find("div", {"class": "elementFont__transformCapitalize"}).text.split(":")[0].strip()
                    metadata_value = data.find("div", {"class": "elementFont__subtitle"}).text.strip()
                    recipe_metadata_values[metadata_text] = metadata_value
                value['metadata'] = recipe_metadata_values
            else:
                value['metadata'] = None
            #Get Directions
            recipe_directions = soup.find_all("fieldset", {"class": "instructions-section__fieldset"})
            if recipe_directions != []:
                for li in recipe_directions[0].find_all("li"):
                    step = li.find('span', {'class': 'elementFont__subtitle--bold'}).text.strip()
                    directions = li.find('div', {'class': 'elementFont__body--paragraphWithin'}).text.strip()
                    value['recipe_directions'] = {step: directions}
            else:
                value['recipe_directions'] = None
                
            #Nutrition Facts
            nutrition_facts = soup.find_all("div", {"class": "recipeNutritionSectionBlock"})
            if nutrition_facts != []:
                nutrition_facts_list = nutrition_facts[0].text.strip().split("Per Serving:")[1].strip().replace(".","").split(";")
                value['recipe_nutrition'] = nutrition_facts_list
            else:
                value['recipe_nutrition'] = None
                
            #break
        
        df = pd.DataFrame.from_dict(data=self.recipes, orient='index')
        df.to_csv(f'recipe_data/recipe_data_{self.keyword}.csv')
    
        return  df
    
    

                  
    
            


