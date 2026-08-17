.PHONY: setup test run

setup:
	uv venv .venv
	uv pip install --python .venv/bin/python -r requirements.txt

test:
	.venv/bin/python -m pytest tests/ -v

run:
	.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8100
