default:
	@make -C master

all:
	@make util
	@make -C master
	@make -C auth

build:
	@make -C worker build
	@make -C master build
	@make -C auth build
	
publish:
	@make -C worker publish
	@make -C master publish
	@make -C auth publish

appclean:
	@kubectl delete deployment master

util:
	@kubectl apply -f zookeper/
	@kubectl wait --for=condition=ready pod zk-0 -n sad --timeout=120s
	@kubectl wait --for=condition=ready pod zk-1 -n sad --timeout=120s
	@kubectl wait --for=condition=ready pod zk-2 -n sad --timeout=120s
	@make -C auth

cleanutil:
	@kubectl delete --all all --namespace=sad
	@kubectl delete pvc datadir-zk-2 datadir-zk-1 datadir-zk-0
