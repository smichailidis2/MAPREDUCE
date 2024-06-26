default:
	@make -C master
	
build:
	@make -C worker
	@make -C master build

appclean:
	@kubectl delete deployment master

zoo:
	@kubectl apply -f zookeper/

clean:
	@kubectl delete --all all --namespace=sad
	@kubectl delete pvc datadir-zk-2 datadir-zk-1 datadir-zk-0
