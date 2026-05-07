.PHONY: dev ingest eval benchmark deploy-backend deploy-frontend clean

dev:
	cd backend && uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev

ingest:
	cd backend && python scripts/ingest_pubmed.py

eval:
	cd backend && python scripts/generate_eval_set.py

benchmark:
	cd backend && python scripts/run_benchmarks.py

deploy-backend:
	cd backend && railway up

deploy-frontend:
	cd frontend && vercel --prod

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
