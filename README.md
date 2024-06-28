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

Monitor worker pods
kubectl get po -l app=worker -w

Get Worker Logs (alive 5 secs after completing)
kubectl logs -l app=worker

Whene done test job will stay alive for 30 seconds
get output with
kubectl logs -l app=run-client-script