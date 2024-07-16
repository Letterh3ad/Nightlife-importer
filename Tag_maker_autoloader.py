import pandas as pd
import os
import re
import requests

basefile = (os.getcwd() + "\\").replace("\\", "/")
outputfolder = os.path.join(os.getcwd(), basefile + "categories_updated/")
import_folder = basefile + "categories/"
download_files_txt = "categories_list.txt"
download_files_path = os.path.join(os.getcwd(), basefile + download_files_txt)

def pathcheck(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"Directory created: {path}")

def import_files(file_path):
    groupings = []
    groupings_names = []
    with open(file_path, 'r') as file:
        current_group = None
        current_group_name = None
        for line in file:
            line = line.strip()
            if line.startswith("#") and line.endswith("["):
                current_group = []
                current_group_name = line[1:-1].strip()
            elif line == "]":
                if current_group:
                    groupings.append(current_group)
                    groupings_names.append(current_group_name)
                current_group = None
                current_group_name = None
            else:
                if current_group is not None:
                    current_group.append(line)
                else:
                    groupings.append([line])
                    group_name = line.split('=')[0].strip()
                    groupings_names.append(group_name)
    print(groupings)
    print(groupings_names)
    return groupings, groupings_names

def download_csv(url, output_folder, output_filename):
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, output_filename)

    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(output_file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded file saved to {output_file_path}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return array_mod_core(output_file_path)

def array_mod_core(csv_path):
    prod_name = "unit_name"
    prod_price = "price"
    prod_net_weight = "package_weight_(shipping)"
    prod_stock_level = "stock"
    rrp = "unit_rrp"
    
    category_list = pd.read_csv(csv_path, sep=',')
    category_list = row_normalizer(category_list, "Family")
    replace_spaces_in_column_names(category_list)
    stock_normalizer(category_list, prod_stock_level)
    category_list['unit_price'] = category_list['unit_price'].astype(int)
    price_set(category_list,prod_price,prod_net_weight)
    
    unitnames = category_list[prod_name].values
    return tag_generator(unitnames, category_list)

def tag_generator(arr, csv_file):
    arr = list(map(str.lower, arr))
    results = {'tags': []}
    
    for item in arr:
        tags = []
        weight_match = re.search(r'(\d+(?:kg|g))', item)
        if weight_match:
            tags.append(weight_match.group(1))
            item = re.sub(r'\d+(?:kg|g)', '', item).strip()

        number_match = re.search(r'x(\d+)', item)
        if number_match:
            tags.append('x' + number_match.group(1))
            item = re.sub(r'x(\d+)', '', item).strip()
        
        colors = [color.strip() for color in item.split(' - ') if color.strip()]
        tags.extend(colors)
        tags_str = ', '.join(tags)
        
        results['tags'].append(tags_str)
    
    return update_tags(results, csv_file)
            
def row_normalizer(dataframe, col_name):
    dataframe[col_name] = dataframe[col_name].str.lower()
    return dataframe

def stock_normalizer(df, col_name):
    df[col_name] = df[col_name].apply(lambda x: 'outofstock' if x == 'OutofStock' else 'instock')

def replace_spaces_in_column_names(dataframe):
    new_column_names = {col: col.lower().replace(' ', '_') for col in dataframe.columns}    
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


def update_tags(tag_dict, csv_file):
    csv_file['tags'] = tag_dict['tags']
    return csv_file

def pandas_to_csv(dataframe, outputfolder, outputname):
    outputfile = os.path.join(outputfolder, outputname)
    dataframe.to_csv(outputfile, sep=',')

pathcheck(outputfolder)
pathcheck(import_folder)
groupings, groupings_names = import_files(download_files_path)

for group, group_name in zip(groupings, groupings_names):
    dataframes = []
    for item in group:
        output_name, download_link = item.strip().split("=", 1)
        output_name = output_name + ".csv"
        csv_file = download_csv(download_link, import_folder, output_name)
        dataframes.append(csv_file)
        print(f"Downloaded and read CSV: {output_name}")
    
    if dataframes:
        concatenated_df = pd.concat(dataframes, ignore_index=True)
        group_output_name = f"{group_name}.csv"
        pandas_to_csv(concatenated_df, outputfolder, group_output_name)
        print(f"Saved concatenated CSV for group: {group_output_name}")
