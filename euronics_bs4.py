from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

ProductInfo = dict[str, list[str | float | int]]


def write_to_csv(
    category_name: str, df: pd.DataFrame, folder_path: str = "euronics/"
) -> None:
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)
    df.to_csv(folder / f"{category_name}.csv", index=False)


def get_soup(
    url: str,
) -> BeautifulSoup:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_links_and_category_names(url: str) -> tuple[list[str], list[str]]:
    offers_soup = get_soup(url)
    box = offers_soup.find("ul", class_="categories__list")

    links = [
        link["href"] for link in box.find_all("a", class_="category__link", href=True)
    ]

    category_names = [
        name.get_text(strip=True).replace(" ", "_")
        for name in box.find_all("div", class_="category-name")
    ]

    return links, category_names


def get_products(url: str) -> ResultSet[Tag]:
    category_soup = get_soup(url)
    category_box = category_soup.find("section", class_="product-card__list")
    return category_box.find_all("article", class_="product-card")


# ? alternative function if you don't want to use &page=1000
# def get_page_number(url: str) -> int:
#     page_extension = "&page="
#     page = 1
#     while True:
#         soup = get_soup(url + page_extension + str(page))
#         print(category_url + page_extension + str(page))

#         if soup.find("a", id="nextAnchor"):
#             page += 1
#         else:
#             return page


def extract_product_info(product: Tag, product_info: dict[str, list]) -> ProductInfo:
    product_info["name"].append(
        product.find("span", class_="product-card__title").get_text(strip=True)
    )

    product_info["img"].append(product.find("img", class_="product-card__image")["src"])

    discount_price = product.select_one(".price br").next_sibling.strip()

    try:
        discount_price_cents = product.select_one(".price span.cp").get_text(strip=True)

        discount_price += discount_price_cents
    except AttributeError:
        pass
    discount_price = discount_price.split()[0]
    product_info["discount_price"].append(discount_price)

    try:
        regular_price = (
            product.find("div", class_="discount__old")
            .get_text(strip=True)
            .split(":")[1]
            .split()[0]
        )

        discount_price_float = float(discount_price)
        regular_price_float = float(regular_price)

        discount_percentage = round(
            ((regular_price_float - discount_price_float) / regular_price_float) * 100,
            1,
        )

    except AttributeError:
        discount_percentage = "N/A"
        regular_price = "N/A"

    product_info["regular_price"].append(regular_price)
    product_info["discount_percentage"].append(discount_percentage)
    product_info["product_link"].append(
        product.find("a", class_="product_name")["href"]
    )

    return product_info


def main() -> None:
    for i, category_url in enumerate(links):
        product_info: ProductInfo = {
            "name": [],
            "product_link": [],
            "img": [],
            "regular_price": [],
            "discount_price": [],
            "discount_percentage": [],
        }

        products = get_products(category_url + max_page_param)
        for product in products:
            product_info = extract_product_info(product, product_info)
        write_to_csv(category_names[i], pd.DataFrame(product_info))


if __name__ == "__main__":
    website = "https://www.euronics.ee"
    offers_path = "/pakkumised"
    links, category_names = get_links_and_category_names(website + offers_path)
    max_page_param = "&page=100"
    main()
