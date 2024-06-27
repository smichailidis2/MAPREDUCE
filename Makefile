default:
	@make -C master

all:
	@make util
	@make -C master
	@make authe
	@make cli

build:
	@make -C worker build
	@make -C master build
	@make -C auth build
	@make -C cli build
	
publish:
	@make -C worker publish
	@make -C master publish
	@make -C auth publish
	@make -C cli publish

appclean:
	@kubectl delete deployment master

util:
	@make zoo
	@make authe
	@make cli

cli:
	@make -C cli

zoo:
	@kubectl apply -f zookeper/
	@kubectl wait --for=condition=ready pod zk-0 -n sad --timeout=120s
	@kubectl wait --for=condition=ready pod zk-1 -n sad --timeout=120s
	@kubectl wait --for=condition=ready pod zk-2 -n sad --timeout=120s

authe:
	@kubectl delete pod flask-app-pod --ignore-not-found=true -n sad
	@make -C auth

cleanall:
	@kubectl delete --all all --namespace=sad
	@kubectl delete pvc datadir-zk-2 datadir-zk-1 datadir-zk-0 --ignore-not-found=true -n sad
