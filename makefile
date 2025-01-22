clean:
	docker compose down -v
	docker image rm paraguayan-products-miner_api
	docker image rm paraguayan-products-miner_miner_tupi
	docker image rm paraguayan-products-miner_miner_arete
	docker image rm paraguayan-products-miner_miner_biggie
	docker image rm paraguayan-products-miner_miner_casarica

run:
	docker compose up --build