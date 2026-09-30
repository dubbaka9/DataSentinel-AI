.PHONY: install run test demo

install:
	python -m pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest -q

demo:
	python scripts/run_demo.py
