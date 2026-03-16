migrate:
	docker exec -it finflow-api alembic revision --autogenerate -m "$(msg)"

upgrade:
	docker exec -it finflow-api alembic upgrade head