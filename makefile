clean:
	docker compose down -v
	docker image rm paraguayan-products-miner_api
	docker image rm paraguayan-products-miner_miner_arete
	docker image rm paraguayan-products-miner_miner_biggie
	docker image rm paraguayan-products-miner_miner_casarica
	docker image rm paraguayan-products-miner_miner_fortis
	docker image rm paraguayan-products-miner_miner_gg
	docker image rm paraguayan-products-miner_miner_nissei
	docker image rm paraguayan-products-miner_miner_stock
	docker image rm paraguayan-products-miner_miner_tupi

run:
	docker compose up --build
