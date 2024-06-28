default:
	@kubectl delete pod cli-interface -n sad
	@kubectl apply -f .

build:
	@docker build -t dkeramidas1/cli_node:v01 .

publish:
	@docker push dkeramidas1/cli_node:v01
	
