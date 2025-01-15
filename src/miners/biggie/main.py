import requests
import concurrent.futures
from dataclasses import dataclass
from unidecode import unidecode
from hashlib import md5

@dataclass
class Category:
    id: int
    name: str
    slug: str
    url: str = 'https://api.app.biggie.com.py/api/articles?take=50&skip=0&classificationName={slug}'

@dataclass
class Product:
    md5: str
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
    
def mine_category(category: Category) -> (list[Product] | None):
    '''
    Mine products from a category, operates like a thread function to not overload the API

    Args:
        category: Category object to mine products from

    Returns:
        list[Product]: List of Product objects mined from the category
        None: If error occurs
    '''
    products_list: list[Product] = []
    while True:
        try:
            response = requests.get(f'https://api.app.biggie.com.py/api/articles?take=50&skip={len(products_list)}&classificationName={category.slug}')
            if response.status_code == 200:
                products = response.json()
                if products['items']:
                    for product in products['items']:
                        url: str = f"https://biggie.com.py/item/{unidecode(product['name'].lower()).replace(' ', '-')}-{product['code']}"
                        md5_code = md5(url.encode()).hexdigest()
                        products_list.append(Product(md5_code,
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
        products_list: list[Product] = []
        print('[DEBUG] Mining products from categories...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for category in categories:
                products_list.extend(executor.submit(mine_category, category).result())

        print(f"[DEBUG] Total products retreived: {len(products_list)}")

        # send a request to the API to save the products
        try:
            response = requests.post('http://api:8080/products/', json=[product.__dict__ for product in products_list])
            if response.status_code == 201:
                print('[DEBUG] Products sent to the API...')
            else:
                print('[ERROR] Failed to send products to the API...')
                print(response.status_code)
        except Exception as e:
            print('[ERROR] Failed to send products to the API...')
            print(e)


    else:
        print('[ERROR] Failed to retreive categories from Biggie API...')

if __name__ == '__main__':
    print('[DEBUG] Starting Biggie Miner...')
    main()
    print('[DEBUG] Biggie Miner finished...')
    
    