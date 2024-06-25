default:
	@make -C master
	
build:
	@make -C worker
	@make -C master build

zoo:
	@cd filesystem; ./setup-nfs.sh


clean:
	@kubectl delete --all all --namespace=sad
	@kubectl delete pvc nfs-pvc
