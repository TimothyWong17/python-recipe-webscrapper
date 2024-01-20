from recipe_scrapper import RecipeScrapper
import pandas as pd
import os
import spacy
import re
import numpy as np
import string



# df_chicken = RecipeScrapper('chicken').get_data()
# df_salmon = RecipeScrapper('salmon').get_data()
# df_beef = RecipeScrapper('beef').get_data()
# df_eggs = RecipeScrapper('eggs').get_data()
# df_tofu = RecipeScrapper('tofu').get_data()

df = pd.DataFrame()

for filename in os.listdir("recipe_data"):
    data = pd.read_csv(f"recipe_data/{filename}")
    df = pd.concat([df, data])
df = df.rename(columns={'Unnamed: 0': 'recipe_name'})
    
df_ingredients = df[['recipe_name', 'ingredients']]
df_ingredients["ingredients"]  = df_ingredients["ingredients"].fillna("")
df_ingredients["ingredients"] = df_ingredients["ingredients"].apply(lambda x: x[1:-1].split(','))
df_ingredients = df_ingredients.explode('ingredients')



base_model = spacy.load('en_core_web_sm')

measurements = re.compile(r'(bowl|bulb|cube|clove|cup|drop|ounce|oz|pinch| inch | pound|teaspoon|tablespoon)s?')
extracted = []
for ix, row in df_ingredients.iterrows():
    print('\r', "Extracting ingredient for row", ix, end='')
    tokens = base_model(row['ingredients'])
    extract = ''
    for token in tokens:
        if (token.dep_ in ['nsubj', 'ROOT', 'dobj']) and (token.pos_ in ['NOUN', 'PROPN', 'ADP']) and (not measurements.match(token.text)):
        #explore children
            for child in token.children:
                if (not measurements.match(child.text)) and (child.dep_ in ['amod', 'compound']):
                    extract += child.text + ' '
            extract += token.text + ' '
    extracted.append(extract)
df_ingredients['ingredient'] = extracted

df_ingredients['ingredient'].replace('', np.nan, inplace=True)
df_ingredients.dropna(subset=['ingredient'], inplace=True)

df_ingredient_counts = pd.DataFrame(df_ingredients.ingredient.value_counts().rename_axis('ingredient').reset_index(name='count'))


df_recipe_ingredients_count = df_ingredients.groupby(['recipe_name', 'ingredient']).count()



recipe_ingredient = df_ingredients.groupby('recipe_name')['ingredient'].apply(set)
recipe_ingredient.head()

ingd_count = {}
for el in df_ingredient_counts.ingredient:
    for r in recipe_ingredient.index:
        if el in recipe_ingredient[r]:
            if el not in ingd_count:
                ingd_count[el] = 1
            else:
                ingd_count[el] += 1
prop_df = pd.DataFrame(ingd_count.items(), columns = ['ingredient', 'proportion'])
prop_df['proportion'] = prop_df['proportion'].div(len(df))
prop_df.sort_values( by = 'proportion', ascending = False)

results_df = pd.merge(df_ingredient_counts, prop_df, on = 'ingredient')
print(results_df.iloc[:20, :])
results_df.iloc[:20, :].to_csv('top_20_ingredients.csv')