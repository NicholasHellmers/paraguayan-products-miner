clean:
	docker compose down -v
	docker image rm paraguayan-products-miner_miner_casarica
	docker image rm paraguayan-products-miner_miner_biggie
	docker image rm paraguayan-products-miner_api

run:
	docker compose up --build