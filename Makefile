up:
	docker compose up --build

down:
	docker compose down

seed:
	docker compose exec backend python -m app.seed

test:
	docker compose exec backend pytest -q
