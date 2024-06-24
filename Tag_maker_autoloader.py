import pandas as pd
import os
import re
import requests


basefile = (os.getcwd()+"\\").replace("\\","/")
outputfolder = os.path.join(os.getcwd(), basefile+"categories_updated/")
import_folder = basefile+"categories/"






#category_list = pd.read_csv(category_file, sep=',')
#unitnames = category_list["Unit Name"].values

download_files_txt = "categories_list.txt"
download_files_path = os.path.join(os.getcwd(), basefile+download_files_txt)

def import_files(file_path):
    print(file_path)
    print(os.path.isfile(file_path))
    with open(file_path, 'r') as file:
        for line in file:
            output_name, download_link = line.strip().split("=", 1)
            output_name = output_name + ".csv"
            download_csv(download_link, import_folder, output_name)
        

def download_csv(url, output_folder, output_filename):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Full path to save the file
    output_file_path = os.path.join(output_folder, output_filename)

    try:
        # Send a HTTP request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Write the content of the response to a file
        with open(output_file_path, 'wb') as file:
            file.write(response.content)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    csv_path = output_folder+output_filename
    tag_array_gen(csv_path,output_filename)

def tag_array_gen(csv_path,output_filename):
    category_list = pd.read_csv(csv_path, sep=',')
    category_list=row_normalizer(category_list,"Family")
    print(category_list)
    unitnames = category_list["Unit Name"].values
    tag_generator(unitnames,category_list,output_filename)
    
def tag_generator(arr, csv_file, output_filename):
    arr = list(map(str.lower, arr))
    results = {
        'tags': []
    }
    
    for item in arr:
        tags = []

        # Extract weight
        weight_match = re.search(r'(\d+(?:kg|g))', item)
        if weight_match:
            tags.append(weight_match.group(1))
            # Remove weight from the string to isolate the color(s)
            item = re.sub(r'\d+(?:kg|g)', '', item).strip()
        
        # Split remaining string by " - "
        colors = [color.strip() for color in item.split(' - ') if color.strip()]
        
        # Append colors to tags
        tags.extend(colors)
        
        # Join tags into a single string separated by commas
        tags_str = ', '.join(tags)
        
        # Append the concatenated tags to the results dictionary
        results['tags'].append(tags_str)
    
    # Print the results for debugging
    print(results)    
    # Update tags in the CSV file
    update_tags(results, csv_file, output_filename)
            
def row_normalizer(dataframe,col_name):
    dataframe[col_name] = dataframe[col_name].str.lower()
    return dataframe
        
def update_tags(tag_dict, csv_file, output_filename):   
    csv_file['tags'] = tag_dict['tags']
    pandas_to_csv(csv_file, outputfolder, output_filename)

def pathcheck(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print("Dir created")

def pandas_to_csv(dataframe,outputfolder,outputname):
    outputfile = os.path.join(outputfolder, outputname)
    dataframe.to_csv(outputfile, sep=',')

pathcheck(outputfolder)
pathcheck(import_folder)
import_files(download_files_path)

