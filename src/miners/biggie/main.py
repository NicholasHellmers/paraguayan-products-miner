import requests
import concurrent.futures
from dataclasses import dataclass
from unidecode import unidecode
from hashlib import sha256
from time import sleep
import random

@dataclass
class Category:
    id: int
    name: str
    slug: str
    url: str = 'https://api.app.biggie.com.py/api/articles?take=50&skip=0&classificationName={slug}'

@dataclass
class Product:
    id: str
    origin: str
    code: str
    name: str
    price: int
    is_discounted: bool
    image_url: str
    product_url: str
    category_name: str

def get_categories() -> (list[Category] | None):
    '''
    Retreive all categories from Biggie API, return a list of Category objects

    Returns:
        list[Category]: List of Category objects
        None: If error occurs
    '''
    try:
        response = requests.get('https://api.app.biggie.com.py/api/classifications/web?take=-1')
        if response.status_code == 200:
            print('[DEBUG] Retreived categories from Biggie API successfully...')
            categories = response.json()
            categories_list: list[Category] = []
            for category in categories['items']:
                categories_list.append(Category(category['id'], category['name'].strip(), category['slug']))
            return categories_list
        else:
            print('[ERROR] Invalid response from Biggie API...')
            print(response.status_code)
            return None
    except Exception as e:
        print('[ERROR] Failed to retreive categories from Biggie API...', e)
        return None
    
def mine_products(category: Category) -> (list[Product] | None):
    '''
    Mine products from a category, operates like a thread function to not overload the API

    Args:
        category: Category object to mine products from

    Returns:
        list[Product]: List of Product objects mined from the category
        None: If error occurs
    '''
    print(f'[DEBUG] Mining products from {category.name} category...')

    sleep(random.randint(0, 5))

    products_list: list[Product] = []
    while True:
        try:
            response = requests.get(f'https://api.app.biggie.com.py/api/articles?take=50&skip={len(products_list)}&classificationName={category.slug}', timeout=120)
            if response.status_code == 200:
                products = response.json()
                if products['items']:
                    for product in products['items']:
                        url: str = f"https://biggie.com.py/item/{unidecode(product['name'].lower()).replace(' ', '-')}-{product['code']}"
                        sha256_code = sha256(url.encode()).hexdigest()
                        products_list.append(Product(sha256_code,
                                                     'biggie',
                                                     product['code'], 
                                                     product['name'],
                                                     product['price'], 
                                                     product['isOnOffer'], 
                                                     product['images'][0]['src'] if product['images'] else "https://biggie.com.py/_nuxt/img/bdefault1.2002ae6.png",
                                                     url, 
                                                     category.name))

                else:
                    print(f'[DEBUG] No products found in {category.name} category...') if not products_list else print(f'[DEBUG] All products from {category.name} category retreived, total of {len(products_list)}...')
                    break
            else:
                print(f'[ERROR] Failed to retreive products from {category.name} category...')
                print(response.status_code)
                return None

        except Exception as e:
            print(f'[ERROR] Failed to retreive products from {category.name} category...')
            print(e)
            return None

    return products_list

def main():

    categories: list[Category] = get_categories()
    print(f'[DEBUG] {categories}')
    if categories:
        print('[DEBUG] Categories retreived successfully...')
        print('[DEBUG] Mining products from categories...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            product_tracker: dict[str, Product] = {}

            futures = [executor.submit(mine_products, category) for category in categories]

            for future in concurrent.futures.as_completed(futures):
                print(f"[DEBUG] Total products retreived: {len(future.result())}")

                if future.result() is not None:
                    for product in future.result():
                        if product.id not in product_tracker:
                            product_tracker[product.id] = product
                        else:
                            continue

            print(f"[DEBUG] Found a total of {len(product_tracker)} products from Biggie...")

            for i in range(0, len(product_tracker), 1000):
                try:
                    print(f"[DEBUG] Sending {i} to {i+1000} products to the API...")
                    response = requests.post('http://api:8080/products/', json=[product.__dict__ for product in list(product_tracker.values())[i:i+1000]], timeout=120)

                    if response.status_code == 201:
                        print('[DEBUG] Products sent to the API...')
                    else:
                        print('[ERROR] Failed to send products to the API...')
                        print(response.status_code)
                        continue

                except Exception as e:
                    print('[ERROR] Failed to send products to the API...', e)


    else:
        print('[ERROR] Failed to retreive categories from Biggie API...')

if __name__ == '__main__':
    print('[DEBUG] Starting Biggie Miner...')
    main()
    print('[DEBUG] Biggie Miner finished...')
    
    