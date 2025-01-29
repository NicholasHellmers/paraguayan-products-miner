import requests
import concurrent.futures
from dataclasses import dataclass
from unidecode import unidecode
from urllib.parse import urlparse
from hashlib import sha256
from bs4 import BeautifulSoup

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
    Retreive all categories from the Superseis main page, with BeautifulSoup, parse the HTML, and return a list of Category objects

    Returns:
        list[Category]: List of Category objects
        None: If error occurs
    '''
    print("[DEBUG] Getting categories from Superseis main page...")

    try:
        request = requests.get('https://superseis.com.py/default.aspx')

        if request.status_code == 200:
            print("[DEBUG] Categories retreived successfully...")
            soup = BeautifulSoup(request.text, 'lxml')

            categories = soup.find_all('ul', class_='catnav wstabitem clearfix')[0].find_all('a')

            categories_list: list[Category] = []

            for category in categories:
                # check if category has href attribute
                if category.has_attr('href'):
                    categories_list.append(Category(
                        name=category.text.strip(),
                        slug=urlparse(category['href']).path,
                        url=f"{category['href']}?pageindex="
                    ))

            return categories_list
        
    except Exception as e:
        print("[ERROR] Failed to retreive categories from Superseis...", e)
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
    print(f'[DEBUG] Mining products from {category.name} category...')
    try:
        category_products: list[Product] = []

        page_number = 1
        while True:
            response = requests.get(f'{category.url}{page_number}', timeout=120)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                products = soup.find_all('div', class_='col-lg-2 col-md-3 col-sm-4 col-xs-6 producto')

                if len(products) == 0 and len(category_products) == 0:
                    print(f'[DEBUG] {len(products)} products found in the {category.name} category...')
                    return category_products
                
                elif len(products) == 0:
                    print(f'[DEBUG] {len(category_products)} products found in the {category.name} category...')
                    return category_products

                for product in products:
                    try:
                        name = product.find('a', class_='product-title-link').text.strip()
                        price = int(product.find('div', class_='prices').find_all('span', class_='price-label')[0].text.replace('.', '').strip())
                        image_url = product.find('a', class_='picture-link').find('img')['src']
                        product_url = product.find('a', class_='product-title-link')['href']
                        is_discounted = False if product.find('div', class_='prices').find_all('span', class_='price-label') == 1 else True

                        category_products.append(Product(
                            id=sha256(product_url.encode()).hexdigest(),
                            origin='Superseis',
                            name=unidecode(name),
                            price=price,
                            is_discounted=is_discounted,
                            image_url=image_url,
                            product_url=product_url,
                            category_name=category.name
                        ))

                    except Exception as e:
                        print(f'[ERROR] Failed to parse product on: {category.url}{page_number}, {e}')
                        continue

            else:
                print(f'[ERROR] Invalid response from {category.name} category...')
                print(response.status_code)

            page_number += 1

    except Exception as e:
        print("[ERROR] Failed to mine products from Superseis...", e)
        return None
        


def main():
    categories: list[Category] = get_categories()[:10]

    categories = sorted(categories, key=lambda x: x.slug, reverse=True)

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
    print("[DEBUG] Running Superseis Miner...")
    main()
    print("[DEBUG] Superseis Miner finished...")