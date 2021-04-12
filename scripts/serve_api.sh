#!/usr/bin/env bash
set -e
if [ "$1" = "--generate-new-schemas" ]; then
	echo "Generating new services API request schemas..."
	./generate_services_api_request_schemas.py
	echo "New schemas created."
	echo "Dereferencing ../diavlos/web/openapi.yaml..."
	swagger-cli bundle --dereference --type yaml ../diavlos/web/openapi.yaml --outfile ../diavlos/web/openapi-dereferenced.yaml
	swagger-cli validate ../diavlos/web/openapi-dereferenced.yaml
fi
../diavlos/web/api.py