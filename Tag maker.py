import pandas as pd
import os
import re

basefile = f"C:/Users/lette/Desktop/Nightlife/Nightlife-importer/"

importfile = "category_20240623.csv"
import_folder = basefile+"categories/"
category_file = os.path.join(os.getcwd(), import_folder, importfile)
#imortfile = "categories_list.txt"
outputfolder = os.path.join(os.getcwd(), basefile+"categories_updated/")
outputname = "tea50g.csv"

print(category_file)
print(os.path.exists(category_file))


category_list = pd.read_csv(category_file, sep=',')
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
            

os.makedirs(outputfolder, exist_ok=True)
output_path = os.path.join(outputfolder, outputname)
category_list.to_csv(output_path, sep=',')

#def csv_sys_import(file)
    
#print(tag_generator(unitnames))

