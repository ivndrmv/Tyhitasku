# ! euronics has the 'hea hind' and so that if i can filter out the products which has only 'hea hind'
# ! i can get rid of try expect in calculating percentage cases if i want to. Just need to agree that 'hea hind'
# ! is classified as discount in our website or not, thats it
# ! can do it with this:  if product.select_one(".price").find_next().get_text(strip=True).startswith('H'): continue -> returns back/up to loop skipping this product
# ! or use product.find("span", "label").get_text().startswith("H") the first one is better because its more specific

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
# i for choosing the category name when we create the cvs files
for i, category_url in enumerate(links):
    product_title = []
    product_img = []
    product_regular_price = []
    product_discount_price = []
    product_discount_percentage = []
    product_link = []
    category_url_result = requests.get(category_url + max_page_nr)
    category_url_content = category_url_result.text
    category_soup = BeautifulSoup(category_url_content, "lxml")
    # if category_url == "https://www.euronics.ee/kampaaniad/pysikliendipakkumised?f=UBA":
    # print(category_soup.find("h1", class_="campaign-heading").get_text())
    category_box = category_soup.find("section", class_="product-card__list")
    products = category_box.find_all("article", class_="product-card")
    # enumerating to keep track which index of product we have to cal the discount price percentage
    for j, product in enumerate(products):
        # print(product.find("span", "label").get_text().startswith("H"))
        product_title.append(
            product.find("span", class_="product-card__title").get_text(strip=True)
        )
        # can use strip but not necessary
        product_img.append(product.find("img", class_="product-card__image")["src"])
        # print(product.get_text(strip=True, separator="\n").strip().split("\n"))
        # css .price br mean select element br which is child of .price, There is only one such element in .price children and lower
        discount_price = product.select_one(".price br").next_sibling.strip()

        # ? sometimes we dont have the cents
        try:
            discount_price_cents = product.select_one(".price span.cp").get_text(
                strip=True
            )

            discount_price += discount_price_cents
        except AttributeError:
            pass

        # ? removing the  space and the € symbol using split method
        product_discount_price.append(discount_price.split()[0])

        # ? sometimes we dont have the regular price displayed
        # ! we can only calculate the discount percentage if we have regular price variable
        # ! that's why the calculation happens inside this
        # ! note that before calculating we need to append new regular price if it exist to product_regular_price
        # ! if we dont find the regular price we just simply add value 'False' to both product_regular_price and product_discount_percentage
        try:
            # ? removing the  space and the € symbol using split method, and many more
            regular_price = (
                product.find("div", class_="discount__old")
                .get_text(strip=True)
                # .replace(" ", "")
                # .replace("\n", "")
                # before: Tavahind:        1329 € -> after 1329 €
                .split(":")[1]
                # before: 1329 € -> after 1329
                .split()[0]
            )

            # product_discount_percentage.append(
            #     round(float(product_discount_price[j].split()[0]))
            #     / float(product_regular_price[j].split[0]),
            #     2,
            # )
            product_regular_price.append(regular_price)
            # print(float(product_discount_price[j].split()[0]))
            # print("regular", float(product_regular_price[j].split()[0]))
            # print(j)
            #
            # ? concert to float only now because before we needed only to alter the str not calculate sth
            discount_price_float = float(product_discount_price[j])
            regular_price_float = float(product_regular_price[j])
            product_discount_percentage.append(
                round(
                    ((regular_price_float - discount_price_float) / regular_price_float)
                    * 100,
                    1,
                )
            )
        except AttributeError:
            # ! AttributeError comes when we can't find the regular_price
            product_discount_percentage.append("False")
            product_regular_price.append("False")

        product_link.append(
            product.select_one("div", class_="product-card__overlays campaign").find(
                "a"
            )["href"]
        )

    # direct_text = product.find(string=True, recursive=False)
    # print(direct_text.strip() if direct_text else "")
    df = pd.DataFrame(
        {
            "name": product_title,
            "product_link": product_link,
            "img": product_img,
            "regular_price": product_regular_price,
            "discount_price": product_discount_price,
            "discount_percentage": product_discount_percentage,
        }
    )
    df.to_csv(folder / f"{category_names[i]}.csv", index=False)
# ! remember that if product name has ',' in it the cvs would put the "" around text to protect it form displaying tit wrongly
# ! the len of each list must be the same otherwise the pd.DataFrame returns error. So we add the False statement
