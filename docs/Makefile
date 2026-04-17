.PHONY: html deploy

html:
	uv run --extra docs sphinx-build -b html . _build/html

deploy: html
	bash deploy.sh
