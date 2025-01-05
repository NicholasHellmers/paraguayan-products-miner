clean:
	docker compose down -v
	docker image rm paraguayan-products-miner_miner_biggie
	docker image rm paraguayan-products-miner_miner_superseis

run:
	docker compose up