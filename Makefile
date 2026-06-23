S3_BUCKET = s3://docs.makingwithcode.org/retro-console/
CF_DISTRIBUTION = EPA6NHZ2LEH1A

.PHONY: build deploy clean

build:
	uv run --extra docs sphinx-build -b html docs docs/_build/html

deploy: build
	aws s3 sync docs/_build/html $(S3_BUCKET)
	aws cloudfront create-invalidation --distribution-id $(CF_DISTRIBUTION) --paths "/retro-console/*"

clean:
	rm -rf docs/_build
