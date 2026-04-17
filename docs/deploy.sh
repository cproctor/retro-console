aws s3 sync _build/html s3://docs.makingwithcode.org/retro-console/
aws cloudfront create-invalidation --distribution-id EPA6NHZ2LEH1A --paths "/retro-console/*"
