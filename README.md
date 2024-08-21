# Nightlife importer
(Data Engineering Kit V0)
This is an importer and data modification script for woocommerce. the aim is to be able to extract meaningful data from dropshipping such as creating parent and child directories as well as extracting keywords from names to create tags.
This is only a prototype and i aim to create a dynamic tool for modifying data with AI and Intergration and transmutation of data.

Setup:
1. move the repository into its own file (It is recommended to set up a venv when using this tool.)
2. Launch Setup.bat in the specified repository (If in CMD use cd to setup in desired repository)
3. Place links to data sources within categories_list.txt as so [New-dataset-name] = [Link-to-Dataset] If you want to group products use 
#[Group-Name] [
[New-dataset-name1] = [Link-to-Dataset1]
[New-dataset-name2] = [Link-to-Dataset2]
]
4. Modify prod_name, prod_price, prod_net_weight, prod_stock_level, rrp with desired columns in dataset (Assuming all datasets are normalized.
5. Run the script and make sure everything runs as expected.
    