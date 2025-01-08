clean:
	docker compose down -v
	docker image rm paraguayan-products-miner_api

run:
	docker compose up --build