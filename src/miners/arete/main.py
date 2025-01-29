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
    url: str

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
    Retreive all categories from the Arete main page, with BeautifulSoup, parse the HTML, and return a list of Category objects

    Returns:
        list[Category]: List of Category objects
        None: If error occurs
    '''
    try:
        response = requests.get('https://www.arete.com.py/')
        if response.status_code == 200:
            print('[DEBUG] Retreived categories from Arete main page successfully...')
            soup = BeautifulSoup(response.text, 'lxml')
            categories = soup.find_all('ul', id='menu-departments-menu')
            categories_list: list[Category] = []

            # Get all li elements in categories with class "yamm-tfw_ yamm-hw menu-item menu-item-has-children animate-dropdown dropdown-submenu" and "menu-item animate-dropdown"
            for category in categories:
                for li in category.find_all('li', class_=['yamm-tfw_ yamm-hw menu-item menu-item-has-children animate-dropdown dropdown-submenu', 'menu-item animate-dropdown']):
                    a = li.find('a')
                    # Title and href are the name and slug of the category
                    slug: str = a['href'] if "https://www.arete.com.py/" not in a['href'] else urlparse(a['href']).path
                    slug = slug[1:] if slug.startswith('/') else slug
                    categories_list.append(Category(
                        name=a['title'].capitalize(), 
                        slug=slug,
                        url=f'https://www.arete.com.py/{slug}'))

            print(f'[DEBUG] {categories_list}')

            return categories_list
        
        else:
            print('[ERROR] Invalid response from Arete main page...')
            print(response.status_code)
            return None
        
    except Exception as e:
        print('[ERROR] Failed to retreive categories from Arete main page...')
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
    products_list: list[Product] = []

    print(f'[DEBUG] Mining {category.name} with URL {category.url} ...')

    sleep(random.randint(0, 5))
    
    try:
        page_number = 1
        while True:
            response = requests.get(f'{category.url}.{page_number}', timeout=120)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')


                products = soup.find_all('div', 'product')

                # print(f'[DEBUG] Got {len(products)} from {category.url}.{page_number}')

                if len(products) == 0:
                    print(f'[DEBUG] found a total of {len(products_list)} {category.name} category...')
                    return products_list

                # print(f'[DEBUG] {products[0]}')

                for product in products:
                    name = product.find('h2').text
                    prices = [price.text.replace('₲', '').replace('.', '').strip() for price in product.find_all('span', 'amount')]
                    prices = [price for price in prices if price.isnumeric()]
                    price = min(prices)
                    image_url = product.find('img')['data-src'] if "https://www.arete.com.py/" in product.find('img')['data-src'] else 'https://www.arete.com.py/' + product.find('img')['data-src']
                    product_url = 'https://www.arete.com.py/' + product.find('a', 'ecommercepro-LoopProduct-link')['href']
                    is_discounted = True if product.find('span', 'onsale') else False

                    # Generate a sha256 hash for the product
                    product_sha256 = sha256(f'{product_url}'.encode()).hexdigest()
                    products_list.append(Product(
                        id=product_sha256,
                        origin='arete',
                        name=unidecode(name).capitalize(),
                        price=int(price.replace('₲', '').replace('.', '')),
                        is_discounted=is_discounted,
                        image_url=image_url,
                        product_url=product_url,
                        category_name=category.name
                    ))

            else:
                print(f'[ERROR] Invalid response from {category.url}...')
                print(response.status_code)
                return None

            page_number += 1
    
    except Exception as e:
        print('[ERROR] Failed to retreive products from Arete main page...')
        print(e)
        return None
        

def main():
    categories: list[Category] = get_categories()

    if categories:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            product_tracker: dict[str, Product] = {}

            futures = [executor.submit(mine_products, category) for category in categories]

            for future in concurrent.futures.as_completed(futures):
                if future.result() is not None:
                    for product in future.result():
                        if product.id not in product_tracker:
                            product_tracker[product.id] = product
                        else:
                            continue

            print(f"[DEBUG] Found a total of {len(product_tracker)} products from Arete...")

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
        print('[ERROR] Failed to retreive categories from Arete main page...')


    

if __name__ == '__main__':
    print("[DEBUG] Running Arete Miner...")
    main()
    print("[DEBUG] Arete Miner finished...")