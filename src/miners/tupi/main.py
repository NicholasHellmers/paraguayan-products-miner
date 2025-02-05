import requests
import concurrent.futures
from urllib.parse import urlparse
from dataclasses import dataclass
from unidecode import unidecode
from hashlib import sha256
from bs4 import BeautifulSoup
import json
import lxml
from time import sleep
import random

@dataclass
class Category:
    name: str
    slug: str
    urls: list[str]

@dataclass
class Product:
    id: str
    origin: str
    name: str
    price: int
    is_discounted: bool
    image_url: str
    product_url: str
    category_name: str

def get_categories() -> (list[Category] | None):
    '''
    Retreive all categories from the Tupi main page, with BeautifulSoup, parse the HTML, and return a list of Category objects

    Returns:
        list[Category]: List of Category objects
        None: If error occurs
    '''
    categories_list: list[Category] = []
    try:
        response = requests.get('https://tupi.com.py/')
        if response.status_code == 200:
            print('[DEBUG] Retreived categories from Tupi main page successfully...')
            soup = BeautifulSoup(response.text, 'lxml')
            categories = soup.find_all('nav', class_='mp-menu menu_accordion', id='mp-menu')[0].find_all('li', class_='icon icon-arrow-left')

            for category in categories:
                name=category.find('a').text.strip().replace("('", "").replace("')", "")
                # print(f'[DEBUG] {name}')
                slug=category.find('a')['href']
                # print(f'[DEBUG] {slug}')
                url_ids= category.find_all('a', class_='tienesubmenu')
                url_ids = [urlparse(url['href']).path.split("/")[1:4] for url in url_ids ]

                # print(f'[DEBUG] {url_ids}')
                categories_list.append(Category(
                    name=name,
                    slug=slug,
                    urls=[f'https://tupi.com.py/buscar_paginacion.php?id={url_id[1]}&{url_id[0][:len(url_id[0]) - 1]}={url_id[1]}&tamano=15&page=' for url_id in url_ids if len(url_id) == 3]
                ))

            return categories_list
        
        else:
            print('[ERROR] Invalid response from Tupi main page...')
            print(response.status_code)
            return None
        
    except Exception as e:
        print('[ERROR] Failed to retreive categories from Tupi main page...')
        print(e)
        return None
    
def mine_products(category: Category) -> (list[Product] | None):
    '''
    Mine products from a category, operates like a thread function to not overload the website

    Args:
        category: Category object to mine products from

    Returns:
        list[Product]: List of Product objects mined from the category
        None: If error occurs
    '''
    sleep(random.randint(0, 5))

    products_list: list[Product] = []

    try:
        for url in category.urls:
            page_number: int = 1
            while True:
                response = requests.get(f'{url}{page_number}', timeout=120)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')

                    products = soup.find_all('div', class_='product_unit product vista_')

                    # print(f'[DEBUG] Got {len(products)} from {category.url}{page_number}')

                    for product in products:

                        try:
                            name_url = product.find('span', class_='loop-product-categories nombre_producto_ug').find('a')
                            name = name_url.text.replace("ver detalles", "").strip().lower()
                            product_url = name_url['href']
                            price = [ price.text for price in product.find_all('span', class_='amount')][1].split("Gs.")
                            price = [ price.replace(".","").strip() for price in price if price.replace(".","").strip().isnumeric() ]
                            is_discounted = False if len(price) == 1 else True
                            image_url = product.find('div', class_='thumbnail').find('img')['src']
                            product_sha256 = sha256(product_url.encode()).hexdigest()

                            products_list.append(Product(
                                id=product_sha256,
                                origin='tupi',
                                name=name,
                                price=int(min(price)),
                                is_discounted=is_discounted,
                                image_url=image_url,
                                product_url=product_url,
                                category_name=category.name
                            ))
                        except Exception as e:
                            print(f'[ERROR] Failed to parse product: {url}{page_number}, {e}')
                            continue

                    if len(products) == 0:
                        break
                    
                    page_number += 1
                
        print(f'[DEBUG] Found a total of {len(products_list)} {category.name} category...')
        return products_list
                
    except Exception as e:
        print('[ERROR] Failed to mine products from Tupi...')
        print(e, category.name, len(products_list))
        return products_list if len(products_list) > 0 else None
    
def main():
    categories: list[Category] = get_categories()

    # print(f'[DEBUG] {categories}')

    if categories is not None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            product_tracker: dict[str, Product] = {}

            futures = [executor.submit(mine_products, category) for category in categories]

            for future in concurrent.futures.as_completed(futures):
                print(f"[DEBUG] Results from search {len(future.result()) if future.result() is not None else 0} products...")

                if future.result() is not None:
                    for product in future.result():
                        if product.id not in product_tracker:
                            product_tracker[product.id] = product
                        else:
                            continue

            print(f"[DEBUG] Found a total of {len(product_tracker)} products from Superseis...")

            # upload to api, 1000 products at a time
            for i in range(0, len(product_tracker), 1000):
                try:
                    print(f"[DEBUG] Sending {i} to {i+1000} products to the API...")
                    response = requests.post('http://api:8080/products/', json=[product.__dict__ for product in list(product_tracker.values())[i:i+1000]], timeout=120)

                    if response.status_code == 201:
                        print('[DEBUG] Products sent to the API...')
                    else:
                        print('[ERROR] Invalid status code from API...')
                        print(response.status_code)
                        continue
                except Exception as e:
                    print('[ERROR] Failed to send products to the API...', e)
                    continue
                    
    else:
        print('[ERROR] No Categories found on the Superseis front page...')
        
if __name__ == '__main__':
    print("[DEBUG] Running Tupi Miner...")
    main()
    print("[DEBUG] Tupi Miner finished...")