lambda.zip: lambda/**
	./build_lambda.sh

deploy: FORCE lambda.zip
	terraform apply -auto-approve

test_environment:
	mkdir test_environment

test: lambda.zip test_environment
	cd test_environment && \
		unzip -o ../lambda.zip

test_request:
	time curl --data "@./sample_requests/sample_body.json" -H 'Content-Type: application/json' -X POST https://dmnzf0zimi.execute-api.us-east-2.amazonaws.com/webhook_stage/handler

FORCE: ;