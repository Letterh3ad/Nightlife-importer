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
    category_list[['prod_name_raw', 'variation']] = category_list[prod_name].apply(
    lambda x: pd.Series(clean_product_name_and_extract_variation(x))
)
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
        
        if weight < 0.1:
            delivery_fee = 2.79
        elif weight < 3:
            delivery_fee = 2.99
        else:
            delivery_fee = 5.99
            
        final_price = round((base_price + delivery_fee) * 1.20,2)
        new_prices.append(final_price)
        
    dataframe['unit_rrp'] = new_prices        
    return dataframe

def clean_product_name_and_extract_variation(name):
    pattern = re.compile(r'\s*(\d+Kg|\d+g|Large|Medium|Small)\s*', re.IGNORECASE)
    variations = pattern.findall(name)
    cleaned_name = re.sub(pattern, '', name)
    cleaned_name = cleaned_name.strip()
    cleaned_name = re.sub(r'\s*-\s*', ' - ', cleaned_name) 
    variation_str = '|'.join(variations) 

    return cleaned_name, variation_str

def update_tags(tag_dict, csv_file):
    csv_file['tags'] = tag_dict['tags']
    return csv_file



def prepare_for_import(df, product_col='unit_name'):
    # Extract and clean data from the specified column
    df[['prod_name_raw', 'variation']] = df[product_col].apply(
        lambda x: pd.Series(clean_product_name_and_extract_variation(x))
    )
    
    # Replace prefixes 'P-', 'S-', 'M-', 'L-' in 'product_code' with '-'
    df["child_product_code"] = df["product_code"].str.replace('P-', '-', regex=False)
    df["child_product_code"] = df["child_product_code"].str.replace('S-', '-', regex=False)
    df["child_product_code"] = df["child_product_code"].str.replace('M-', '-', regex=False)
    df["child_product_code"] = df["child_product_code"].str.replace('L-', '-', regex=False)
    
    # Sort by 'child_product_code' and reset index
    rslt_df = df.sort_values(by='child_product_code').reset_index(drop=True)
    
    return rslt_df


def create_parent_rows(df):
    # Group by child_product_code and aggregate information
    grouped = df.groupby('child_product_code').agg({
        'prod_name_raw': 'first',
        'variation': lambda x: '|'.join(x),
        'webpage_description_(html)': 'first',
        'webpage_description_(plain_text)': 'first',
        'product_code': 'first',
        '1st_image': 'first'  # Assuming '1st_image' contains the image URL or identifier
    }).reset_index()

    # Create new rows for parent products
    new_rows = []
    parent_code_map = {}
    parent_suffix_counter = {}

    for idx, row in grouped.iterrows():
        base_code = row['product_code']
        
        # Generate a unique suffix for each parent product code
        if base_code not in parent_suffix_counter:
            parent_suffix_counter[base_code] = 1
        else:
            parent_suffix_counter[base_code] += 1
        
        parent_suffix = parent_suffix_counter[base_code]
        parent_code = f"{base_code}-{parent_suffix}"
        
        # Map the base code to the generated parent product code
        parent_code_map[base_code] = parent_code
        
        # Create parent row with the first child's image
        parent_row = {
            'child_product_code': '',  # Parent rows do not have a child_product_code
            'prod_name_raw': row['prod_name_raw'],
            'variation': row['variation'],
            'webpage_description_(html)': row['webpage_description_(html)'],
            'webpage_description_(plain_text)': row['webpage_description_(plain_text)'],
            'product_code': parent_code,
            '1st_image': row['1st_image']  # Assign the image from the first child
        }
        new_rows.append(parent_row)

        # Update child products to use the new parent product code
        df.loc[df['child_product_code'] == row['child_product_code'], 'child_product_code'] = parent_code

    # Convert new rows to DataFrame
    new_rows_df = pd.DataFrame(new_rows)

    # Concatenate new rows with updated original DataFrame
    result_df = pd.concat([new_rows_df, df], ignore_index=True)

    # Sort by child_product_code and ensure parent rows are at the top
    result_df['is_parent'] = result_df.apply(lambda row: row['child_product_code'] in new_rows_df['product_code'].values, axis=1)
    result_df = result_df.sort_values(by=['child_product_code', 'is_parent'], ascending=[True, False]).drop(columns='is_parent').reset_index(drop=True)

    return result_df



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
        variable_df = prepare_for_import(concatenated_df, product_col='unit_name')
        result_df = create_parent_rows(variable_df)
        df_no_duplicates = result_df.drop_duplicates()
        group_output_name = f"{group_name}.csv"
        pandas_to_csv(df_no_duplicates, outputfolder, group_output_name)
        print(f"Saved concatenated CSV for group: {group_output_name}")
