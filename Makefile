.PHONY: up dev-backend dev-frontend test migrate clean

up:
	docker-compose up -d

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && set PYTHONPATH=. && pytest tests/ -v

migrate:
	cd backend && set PYTHONPATH=. && python -m alembic upgrade head

clean:
	docker-compose down -v
	rm -rf backend/flyyy.db backend/test.db
