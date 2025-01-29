# paraguayan-products-miner
Data miner for paraguayan ecommerce products.

## Requirements
- Docker
- Make
- Go

## How to run
1. Clone the repository
2. Create an `.env` file in the root of the project with the following content:
    ```env
    MONGO_URI="mongodb://admin:password@mongo:27017/mongo?authSource=admin"
    MONGO_INITDB_DATABASE="mongo"
    MONGO_INITDB_ROOT_USERNAME="admin"
    MONGO_INITDB_ROOT_PASSWORD="password"
    ```
    This can be changed to your own MongoDB configuration.
3. Run the following command to start the project:
    ```bash
    make run
    ```

4. To clean the project, run the following command:
    ```bash
    make clean
    ```

5. If you're having issues with setting up the API:
    ```bash
    go mod tidy
    ```

## Todo
- [ ] Stores to mine
    - [x] Biggie - [https://www.biggie.com.py/](https://www.biggie.com.py/)
    - [ ] Nueva Americana - [https://www.nuevaamericana.com.py/](https://www.nuevaamericana.com.py/)
    - [x] Casa Rica - [https://www.casarica.com.py/](https://www.casarica.com.py/)
    - [x] Areté - [https://www.arete.com.py/](https://www.arete.com.py/)
    - [ ] Nissei - [https://nissei.com/py/](https://nissei.com/py/)
    - [ ] Superseis - [https://www.superseis.com.py/](https://www.superseis.com.py/)
    - [ ] Stock - [https://www.stock.com.py/](https://www.stock.com.py/)
    - [ ] Hendyla - [https://www.hendyla.com/](https://www.hendyla.com/)
    - [x] Tupi - [https://www.tupi.com.py/](https://www.tupi.com.py/)
    - [x] González Giménez - [https://www.gonzalezgimenez.com/](https://www.gonzalezgimenez.com/)
    - [x] Fortis - [https://www.fortis.com.py/](https://www.fortis.com.py/)
    - [ ] Shopping China - [https://www.shoppingchina.com.py/](https://www.shoppingchina.com.py/)
    - [ ] Bristol - [https://www.bristol.com.py/](https://www.bristol.com.py/)
- [x] MongoDB setup
- [x] Golang API