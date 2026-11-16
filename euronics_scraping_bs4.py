# importing so that later i can write the output to the specific folder
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# making folder that scraped data will go into
folder = Path("euronics/")
folder.mkdir(parents=True, exist_ok=True)

website = "https://www.euronics.ee"
offers_url = f"{website}/pakkumised"
result = requests.get(offers_url)
content = result.text
soup = BeautifulSoup(content, "lxml")

box = soup.find("ul", class_="categories__list")
#  fin all 'a' tags that have class name of "category__link" and have href itself
# also note that link['href'] only works because Beautifulsoup
# Basically says find 'href' attribute and take its value only inside the link item
links = [link["href"] for link in box.find_all("a", class_="category__link", href=True)]
# searching for category names to later have separate cvs file for each category
# Replacing the ' ' whit '_' so that we dont introduce special '\' character basically spaces in file name
# makes it better to extract later
category_names = [
    name.get_text(strip=True).replace(" ", "_")
    for name in box.find_all("div", class_="category-name")
]

# ! good idea to do: find the element //a[@id='nextAnchor'] the button in category url like https://www.euronics.ee/kampaaniad/pysikliendipakkumised?f=UBA&page=7
# ! next step watch the &page=7 so that at page 7 when button disappears the //a[@id='nextAnchor'] style"display: none" will appear
# ! maybe you cold do while loop and try expect with that to find the page and just insert the max page numebr so that appears max number of pages
# ! or you could just say inserts 100 but if it has more that 100 it fails and doesn't look clean
# ? bad one the max_page_nr
max_page_nr = "&page=100"
for i, category in enumerate(links):
    product_title = []
    product_img = []
    product_regular_price = []
    product_discount_price = []
    # product_discount_percentage = []
    category_url = category
    category_url_result = requests.get(category_url + max_page_nr)
    category_url_content = category_url_result.text
    category_soup = BeautifulSoup(category_url_content, "lxml")
    # if category_url == "https://www.euronics.ee/kampaaniad/pysikliendipakkumised?f=UBA":
    # print(category_soup.find("h1", class_="campaign-heading").get_text())
    category_box = category_soup.find("section", class_="product-card__list")
    products = category_box.find_all("article", class_="product-card")
    for product in products:
        product_title.append(
            product.find("span", class_="product-card__title").get_text(strip=True)
        )
        product_img.append(
            product.find("img", class_="product-card__image")["src"].strip()
        )
        # print(product.get_text(strip=True, separator="\n").strip().split("\n"))
        discount_price = product.select_one(".price br").next_sibling.strip()

        # ? sometimes we dont have the cents
        try:
            discount_price_cents = product.select_one(".price span.cp").get_text(
                strip=True
            )
            discount_price += discount_price_cents
        except AttributeError:
            pass

        product_discount_price.append(discount_price)

        # ? sometimes we dont have the regular price displayed
        try:
            regular_price = (
                product.find("div", class_="discount__old")
                .get_text(strip=True)
                .replace(" ", "")
                .replace("\n", "")
                .split(":")[1]
            )
            product_regular_price.append(regular_price)
        except AttributeError:
            product_regular_price.append("False")

    # direct_text = product.find(string=True, recursive=False)
    # print(direct_text.strip() if direct_text else "")
    df = pd.DataFrame(
        {
            "name": product_title,
            "img": product_img,
            "regular_price": product_regular_price,
            "discount_price": product_discount_price,
        }
    )
    df.to_csv(folder / f"{category_names[i]}.csv", index=False)
# ! remember that if product name has ',' in it the cvs would put the "" around text to protect it form displaying tit wrongly
