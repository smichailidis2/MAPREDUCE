default:
	@kubectl apply -f .
	@kubectl rollout restart deployment master

build:
	@docker build -t dkeramidas1/master_node:v01 .

publish:
	@docker push dkeramidas1/master_node:v01
	
