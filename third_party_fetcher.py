import requests
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
FILE_OUT_NAME = "third_fetch.md"

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
    not_found_modules = all_modules_no_somko
    for version in POSSIBLE_VERSIONS:
        url = BASE_URL.replace("VERSION_NUMBER", version)
        url = url.replace("MODULE_NAME", module)
        page = requests.get(url)

        if page.status_code != 404:
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

            # [MODULE_NAME, FULL_URL, COST, VERSION]
            info = [module, url, version, price]
            found_modules.append(info)
            found_temp.append(module)
            not_found_modules = [m for m in all_modules_no_somko if m not in found_temp]
            break
    found_modules.sort(key=lambda m: m[3])


with open(FILE_OUT_NAME, "w") as out_file:
    for module in found_modules:
        out_file.write(f"[{module[0]}]({module[1]}) ({module[2]}) PRICE: {module[3]}")
        out_file.write("\n\n")

    for module in not_found_modules:
        out_file.write(f"{module}: NOT FOUND")
        out_file.write("\n\n")


print(found_modules)
