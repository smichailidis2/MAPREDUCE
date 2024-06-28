default:
	@kubectl apply -f client.yaml

double:
	@kubectl delete job -l app=run-client-script -n sad
	@kubectl apply -f doubletest.yaml

build:
	@docker build -t dkeramidas1/test:v01 .

publish:
	@docker push dkeramidas1/test:v01