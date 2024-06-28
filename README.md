# MAPREDUCE - UI

for testing

On a machine with kubectl and no pods running
make all 
creates the system (zookeeper,athentication,master_node)

Then 
make -C test
executes one test

make -C test double 
executes 2 test in parallel

kubectl get po -l app=worker -w

kubectl logs -l app=worker