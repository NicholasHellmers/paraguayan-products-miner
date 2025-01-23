import requests
import concurrent.futures
from dataclasses import dataclass
from unidecode import unidecode
from hashlib import sha256
import json

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

def get_pages() -> ( int | None):
    '''
    Retreive all categories from the Gonzalez Gimenez main page, with BeautifulSoup, parse the HTML, and return a list of Category objects

    Returns:
        list[Category]: List of Category objects
        None: If error occurs
    '''
    try:
        response = requests.get('https://www.gonzalezgimenez.com.py/get-productos', timeout=120)
        if response.status_code == 200:
            # parse JSON
            data = json.loads(response.text)
            # get total pages
            return data['paginacion']['last_page']
        else:
            print('[ERROR] Invalid response from Gonzalez Gimenez...')
            print(response.status_code)
            return None
    except Exception as e:
        print('[ERROR] Failed to retreive categories from Gonzalez Gimenez...', e)
        return None
    
def mine_products(url: str) -> (list[Product] | None):
    '''
    Mine products from a category, operates like a thread function to not overload the website

    Args:
        category: Category object to mine products from

    Returns:
        list[Product]: List of Product objects mined from the category
        None: If error occurs
    '''
    try:
        response = requests.get(url, timeout=120)

        if response.status_code == 200:
            print(f'[DEBUG] Retreived products from {url} successfully...')
            data = json.loads(response.text)
            products_list: list[Product] = []

            for product in data['paginacion']['data']:
                products_list.append(Product(
                    id=sha256(product['url_ver'].encode()).hexdigest(),
                    origin='Gonzalez Gimenez',
                    name=unidecode(product['nombre']),
                    price=product['getPrecio'] if product['precio_oferta'] == 0 else product['precio_oferta'],
                    is_discounted=True if product['precio_oferta'] != 0 else False,
                    image_url=product['primera_imagen'],
                    product_url=product['url_ver'],
                    category_name=product['producto']['categoria']['nombre']
                ))

            return products_list
        
        else:
            print('[ERROR] Invalid response from Gonzalez Gimenez...')
            print(response.status_code)
            return None
        
    except Exception as e:
        print('[ERROR] Failed to retreive products from Gonzalez Gimenez...')
        print(e)
        return None
    
def main():

    pages: list[str] = [f'https://www.gonzalezgimenez.com.py/get-productos?page={page}' for page in range(1, get_pages() + 1)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(mine_products, page) for page in pages]

        for future in concurrent.futures.as_completed(futures):
            # Send a request to the API to save the products
            try:
                result = future.result()

                print(f"[DEBUG] Total products retreived: {len(result)}")

                if result is not None:
                    response = requests.post('http://api:8080/products/', json=[product.__dict__ for product in result], timeout=120)
                    print(f'[DEBUG] Time taken to send products: {response.elapsed.total_seconds()} seconds...')
                    if response.status_code == 201:
                        print('[DEBUG] Products sent to the API...')
                    else:
                        print('[ERROR] Failed to send products to the API...')
                        print(response.status_code)
                else:
                    print('[ERROR] No products were mined, none were sent to API...')

            except Exception as e:
                print('[ERROR] Failed to send products to the API...', e)

if __name__ == '__main__':
    print("[DEBUG] Running Gonzalez Gimenez Miner...")
    main()
    print("[DEBUG] Gonzalez Gimenez Miner finished...")