import pandas as pd
import os
import re
import requests

basefile = f"C:/Users/lette/Desktop/Nightlife/Nightlife-importer/"
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
    unitnames = category_list["Unit Name"].values
    tag_generator(unitnames,category_list,output_filename)
    
def tag_generator(arr, csv_file, output_filename):
    arr=list(map(str.lower,arr))
    results = {
        'tag1': [],
        'tag2': [],
        'tag3': [],
        'tag4': []
    }
    
    for item in arr:
        tags = [None, None, None, None]
        # Extract weight
        weight_match = re.search(r'(\d+(?:kg|g))', item)
        if weight_match:
            tags[3] = weight_match.group(1)
            # Remove weight from the string to isolate the color(s)
            item = re.sub(r'\d+(?:kg|g)', '', item).strip()
        
        # Split remaining string by " - "
        colors = [color.strip() for color in item.split(' - ') if color.strip()]
        
        # Assign colors to tags
        for i, color in enumerate(colors):
            if i < 3:
                tags[i] = color
        
        # Append the tags to the results dictionary
        results['tag1'].append(tags[0])
        results['tag2'].append(tags[1])
        results['tag3'].append(tags[2])
        results['tag4'].append(tags[3])
    
    # Print the results for debugging
    print(results)
    
    # Update tags in the CSV file
    update_tags(results, csv_file, output_filename)
            

def update_tags(tag_dict,csv_file,output_filename):   
    for i in range(len(tag_dict)):
        tag_id = str("tag"+str(i+1))
        csv_file[tag_id] = tag_dict[tag_id]
    pandas_to_csv(csv_file,outputfolder,output_filename)

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

