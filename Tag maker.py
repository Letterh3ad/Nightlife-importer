import pandas as pd
import os
import re

importfile = "category_20240623.csv"
importfolder = f"C:/Users/lette/Desktop/Nightlife/"
category_folder = os.path.join(os.getcwd(), importfolder+"categories/", importfile)
#imortfile = "categories_list.txt"
outputfolder = os.path.join(os.getcwd(), importfolder, )


category_list = pd.read_csv(category_folder, sep=',')
unitnames = category_list["Unit Name"].values
print(unitnames)
print(len(category_list.columns))

def tag_generator(dataset):
    results = []
    for item in dataset:
        color = None
        weight = None
        
        weight_match = re.search(r'(\d+(?:kg|g))', item)
        if weight_match:
            weight = weight_match.group(1)
            item = re.sub(r'\d+(?:kg|g)', '', item).strip()

        colors = item.split(' - ')
        color = ' - '.join([color.strip() for color in colors if color.strip()])

        results.append([color, weight])
    
    return results
            

category_list.to_csv("out.cvs", sep=',')

#def csv_sys_import(file)
    
aa#print(tag_generator(unitnames))

