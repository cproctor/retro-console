.PHONY: docs deploy

docs:
	uv run --extra docs sphinx-build -b html docs docs/_build/html

deploy: docs
	aws s3 sync docs/_build/html s3://docs.makingwithcode.org/retro-console/
	aws cloudfront create-invalidation --distribution-id EPA6NHZ2LEH1A --paths "/retro-console/*"
