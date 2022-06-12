lambda.zip: lambda/**
	./build_lambda.sh

deploy: FORCE lambda.zip
	terraform apply

test_environment:
	mkdir test_environment

test: lambda.zip test_environment
	cd test_environment && \
		unzip -o ../lambda.zip && \
		cp ../lambda/sample_request*.json .

FORCE: ;