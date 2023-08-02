import requests
import re
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join, isdir

user_path = input("Third party folder path (leave empty for current path)): ")

BASE_URL = "https://apps.odoo.com/apps/modules/VERSION_NUMBER/MODULE_NAME/"
DIR_PATH = "./"
if user_path != "":
    DIR_PATH = user_path
POSSIBLE_VERSIONS = ["16.0", "15.0", "14.0", "13.0", "12.0", "11.0"]
VERSION = 0 # index in possible versions
FILE_OUT_NAME = "third_fetch"

# return if the folder_name follows the somko module naming standard
def is_somko_module(folder_name):
    if len(folder_name) >= 5:
        if folder_name[0:5] == "somko":
            return False
    return folder_name

all_modules = [f for f in listdir(DIR_PATH) if isdir(join(DIR_PATH, f))]
all_modules_no_somko = list(filter(is_somko_module, all_modules))

found_modules = []
found_temp = []
not_found_modules = []

# send requests for all modules and check if they exist
for module in all_modules_no_somko:
    print(f"Searching for {module}")
    not_found_modules = all_modules_no_somko
    
    # Version finding
    local_version = "no version" 
    try:
        with open(f'{DIR_PATH}/{module}/__manifest__.py', 'r') as man:
            lines = man.readlines()
            version_line = ''
            for line in lines:
                if 'version' in line:
                    version_line = line
            version_number = re.findall(r'\d+(?:\.\d+)+', version_line)
            local_version = version_number[0]
    except:
        print(f"No manifest file for {module}")

    # Check for existance and gather info
    for version in POSSIBLE_VERSIONS:
        url = BASE_URL.replace("VERSION_NUMBER", version)
        url = url.replace("MODULE_NAME", module)
        page = requests.get(url)

        if page.status_code != 404:
            print(f"\t Found version for {module}")
            soup = BeautifulSoup(page.content, "html.parser")
            wrap = soup.find(id="wrap")
            price_elements = wrap.find_all("input", class_="js_product_price")

            price = 0
            for element in price_elements:
                price = element.get("value")

            # make it comparable
            if price == None:
                price = 0
            price = float(price)

            # [MODULE_NAME, FULL_URL, VERSION, COST, local_version]
            info = [module, url, version, price, local_version]
            found_modules.append(info)
            found_temp.append(module)
            not_found_modules = [m for m in all_modules_no_somko if m not in found_temp]
            break

    # sort on price
    found_modules.sort(key=lambda m: m[3])


# csv format
with open(FILE_OUT_NAME + '.csv', "w") as out_file:
    top_row = ['Name:', 'Available Version', 'Local Version', 'Price']
    rows = [top_row]


    for module in found_modules:
        row = [f'=HYPERLINK("{module[1]}", "{module[0]}")', f'{module[2]}', f'{module[4]}', f'{module[3]}']
        rows.append(row)

    for row in rows:
        out_file.write(';'.join(row) + '\n')


# md format
with open(FILE_OUT_NAME + '.md', "w") as out_file:
    for module in found_modules:
        out_file.write(f"[{module[0]}]({module[1]}) ({module[2]}) PRICE: {module[3]}")
        out_file.write("\n\n")

    for module in not_found_modules:
        out_file.write(f"{module}: NOT FOUND")
        out_file.write("\n\n")


print(f"Done, files {FILE_OUT_NAME}.md and {FILE_OUT_NAME}.csv generated.")
