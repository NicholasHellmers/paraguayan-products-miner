clean:
	docker compose down -v
	docker image rm paraguayan-products-miner_miner_biggie

run:
	docker compose up