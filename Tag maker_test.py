import pandas as pd
import os
import re
import requests
from collections import defaultdict

basefile = (os.getcwd()+"\\").replace("\\","/")
outputfolder = os.path.join(os.getcwd(), basefile+"categories_updated/")
import_folder = basefile+"categories/"

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
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, output_filename)

    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(output_file_path, 'wb') as file:
            file.write(response.content)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    
    csv_path = os.path.join(output_folder, output_filename)
    array_mod_core(csv_path, output_filename)

def array_mod_core(csv_path, output_filename):
    prod_name = str("unit_name")
    prod_price = str("price")
    prod_net_weight = str("unit_net_weight")
    prod_stock_level = str("stock")
    rrp = str("unit_rrp")

    category_list = pd.read_csv(csv_path, sep=',')
    category_list = row_normalizer(category_list, "Family")
    replace_spaces_in_column_names(category_list)
    print(category_list)
    unitnames = category_list[prod_name].values
    stock_normalizer(category_list, prod_stock_level)
    category_list['unit_price'] = category_list['unit_price'].astype(int)
    category_list = price_set(category_list, prod_price, prod_net_weight, rrp)
    category_list = add_base_name_category(category_list, prod_name)
    tag_generator(unitnames, category_list, output_filename)

def find_consistent_words(dataframe, prod_name_col):
    all_words = dataframe[prod_name_col].str.split().explode().value_counts()
    total_rows = len(dataframe)
    consistent_words = all_words[all_words == total_rows].index.tolist()
    return consistent_words

def add_base_name_category(dataframe, prod_name_col):
    consistent_words = find_consistent_words(dataframe, prod_name_col)
    def extract_base_name(product_name):
        words = product_name.split()
        filtered_words = [word for word in words if word.lower() not in [cw.lower() for cw in consistent_words]]
        base_name = ' '.join(filtered_words)
        return base_name.strip().lower()

    dataframe['base_name_category'] = dataframe[prod_name_col].apply(extract_base_name)
    return dataframe

def tag_generator(arr, csv_file, output_filename):
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
    
    print(results)
    update_tags(results, csv_file, output_filename)
            
def row_normalizer(dataframe, col_name):
    dataframe[col_name] = dataframe[col_name].str.lower()
    return dataframe

def stock_normalizer(df, col_name):
    df[col_name] = df[col_name].apply(lambda x: 'outofstock' if x == 'OutofStock' else 'instock')

def replace_spaces_in_column_names(dataframe):
    new_column_names = {col: col.lower().replace(' ', '_') for col in dataframe.columns}    
    dataframe.rename(columns=new_column_names, inplace=True)
    return dataframe

def price_set(dataframe, col_name, weight_col_name, final_price_location):
    def calculate_final_price(base_price, item_weight):
        weight = item_weight
        if weight < 0.1:
            delivery_fee = 2.79
        elif weight < 3:
            delivery_fee = 2.99
        else:
            delivery_fee = 5.99
        
        final_price = (base_price + delivery_fee) * 1.20
        print(final_price)
        return round(final_price, 2)
    
    temp = []
    for i in range(len(dataframe[col_name])):
        item_weight = dataframe[weight_col_name][i]
        base_price = dataframe[col_name][i]
        print(base_price)
        temp.append(calculate_final_price(base_price, item_weight))
    dataframe[final_price_location] = temp
    
    return dataframe

def update_tags(tag_dict, csv_file, output_filename):
    csv_file['tags'] = tag_dict['tags']
    pandas_to_csv(csv_file, outputfolder, output_filename)

def pathcheck(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print("Dir created")

def pandas_to_csv(dataframe, outputfolder, outputname):
    outputfile = os.path.join(outputfolder, outputname)
    dataframe.to_csv(outputfile, sep=',')

def aggregate_datasets(import_folder, outputfolder):
    dataframes = defaultdict(list)
    for filename in os.listdir(import_folder):
        if filename.endswith('.csv'):
            category = filename.split('_')[0]
            df = pd.read_csv(os.path.join(import_folder, filename))
            df = apply_all_functions(df)
            dataframes[category].append(df)
    
    aggregated_data = {key: pd.concat(dfs) for key, dfs in dataframes.items()}
    for category, df in aggregated_data.items():
        output_filename = f"{category}_aggregated.csv"
        pandas_to_csv(df, outputfolder, output_filename)
        print(f"Aggregated data for {category} saved to {output_filename}")

def apply_all_functions(dataframe):
    prod_name = "unit_name"
    prod_price = "price"
    prod_net_weight = "unit_net_weight"
    prod_stock_level = "stock"
    rrp = "unit_rrp"
    
    dataframe = row_normalizer(dataframe, "Family")
    replace_spaces_in_column_names(dataframe)
    stock_normalizer(dataframe, prod_stock_level)
    dataframe['unit_price'] = dataframe['unit_price'].astype(int)
    dataframe = price_set(dataframe, prod_price, prod_net_weight, rrp)
    dataframe = add_base_name_category(dataframe, prod_name)
    return dataframe

pathcheck(outputfolder)
pathcheck(import_folder)
import_files(download_files_path)
aggregate_datasets(import_folder, outputfolder)


