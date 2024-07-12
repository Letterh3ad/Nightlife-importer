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
    array_mod_core(csv_path,output_filename)

def array_mod_core(csv_path,output_filename):
    #Add dataframe column nammes here (Note: they will be formatted to lower case
    # as well as spaces replaced with "_"
    prod_name = str("unit_name")
    prod_price = str("price")
    prod_net_weight = str("unit_net_weight")
    prod_stock_level = str("stock")
    ##########
    
    category_list = pd.read_csv(csv_path, sep=',')
    category_list=row_normalizer(category_list,"Family")
    replace_spaces_in_column_names(category_list)
    print("DataFrame columns:", category_list.columns)
    print(category_list)
    unitnames = category_list[prod_name].values
    stock_normalizer(category_list,prod_stock_level)
    price_set(category_list,prod_price,prod_net_weight)
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

        number_match = re.search(r'x(\d+)', item)
        if number_match:
            tags.append('x' + number_match.group(1))
            item = re.sub(r'x(\d+)', '', item).strip()
        
        colors = [color.strip() for color in item.split(' - ') if color.strip()]
        
        tags.extend(colors)
        
        tags_str = ', '.join(tags)
        
        results['tags'].append(tags_str)
    
    print(results)    
    update_tags(results, csv_file, output_filename)
            
def row_normalizer(dataframe,col_name):
    dataframe[col_name] = dataframe[col_name].str.lower()
    return dataframe

def stock_normalizer(df,col_name):
    df[col_name] = df[col_name].apply(lambda x: 'outofstock' if x == 'OutofStock' else 'instock')


def replace_spaces_in_column_names(dataframe):
    # Create a dictionary to map old column names to new column names
    new_column_names = {col: col.lower().replace(' ', '_') for col in dataframe.columns}    

    # Rename the columns
    dataframe.rename(columns=new_column_names, inplace=True)
    
    return dataframe

def price_set(dataframe, col_name, weight_col_name):
    new_prices = []
    for i in range(len(dataframe[col_name])):
        base_price = dataframe[col_name][i]
        weight = dataframe[weight_col_name][i]
        
        # Determine the delivery fee based on weight
        if weight < 0.1:
            delivery_fee = 2.79
        elif weight < 3:
            delivery_fee = 2.99
        else:
            delivery_fee = 5.99
            
        # Calculate final price including delivery fee and 20% markup
        final_price = round((base_price + delivery_fee) * 1.20,2)
        new_prices.append(final_price)
        
    dataframe['unit_rrp'] = new_prices        
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

