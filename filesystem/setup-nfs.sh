#setup-nfs.sh
#!/bin/bash

NAMESPACE=sad

echo "Applying namespace configuration..."
kubectl apply -f filesystem/namespace.yaml

kubectl get namespace $NAMESPACE || kubectl create namespace $NAMESPACE

echo "Deleting GlusterFS StatefulSet, service, and PVC if they exist..."
kubectl delete statefulset glusterfs -n $NAMESPACE --ignore-not-found=true
kubectl delete service glusterfs -n $NAMESPACE --ignore-not-found=true
kubectl delete pvc glusterfs-pvc -n $NAMESPACE --ignore-not-found=true
kubectl delete pv glusterfs-pv --ignore-not-found=true

echo "Deleting existing NFS resources if they exist..."
kubectl delete deployment nfs-server -n $NAMESPACE --ignore-not-found=true
kubectl delete service nfs-server -n $NAMESPACE --ignore-not-found=true
kubectl delete pod -l app=nfs-server -n $NAMESPACE --ignore-not-found=true
kubectl patch pvc nfs-pvc -n $NAMESPACE -p '{"metadata":{"finalizers":null}}'
kubectl delete pvc nfs-pvc -n $NAMESPACE --ignore-not-found=true --force --grace-period=0
kubectl delete pv nfs-pv --ignore-not-found=true

echo "Deleting ZooKeeper StatefulSet and associated resources..."
kubectl delete statefulset zookeeper -n $NAMESPACE --ignore-not-found=true
kubectl delete service zookeeper -n $NAMESPACE --ignore-not-found=true
kubectl delete pvc zookeeper-data-zookeeper-0 -n $NAMESPACE --ignore-not-found=true
kubectl delete pvc zookeeper-data-zookeeper-1 -n $NAMESPACE --ignore-not-found=true
kubectl delete pvc zookeeper-data-zookeeper-2 -n $NAMESPACE --ignore-not-found=true

echo "Waiting for NFS PVC to be fully deleted..."
while kubectl get pvc nfs-pvc -n $NAMESPACE &>/dev/null; do
  echo "Waiting for deletion of nfs-pvc..."
  sleep 5
done
echo "NFS PVC deleted successfully."

echo "Waiting for all PVs to be completely cleaned up..."

TIMEOUT=120
ELAPSED=0
SLEEP_INTERVAL=10

while kubectl get pv | grep -q 'Released\|Bound'; do
  echo "Waiting for all PVs to be completely cleaned up..."
  sleep $SLEEP_INTERVAL
  ELAPSED=$((ELAPSED + SLEEP_INTERVAL))
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "Timeout reached. Forcibly deleting any remaining PVs."
    kubectl get pv | grep 'Released\|Bound' | awk '{print $1}' | xargs kubectl delete pv --force --grace-period=0
    break
  fi
done

echo "Applying NFS server service and deployment..."
kubectl apply -f filesystem/nfs/nfs-service.yaml -n $NAMESPACE
kubectl apply -f filesystem/nfs/nfs-deployment.yaml -n $NAMESPACE

#echo "Waiting for NFS server to be ready..."
#kubectl wait --for=condition=ready pod -l app=nfs-server -n $NAMESPACE --timeout=300s

echo "Applying Persistent Volume and Persistent Volume Claim..."
kubectl apply -f filesystem/nfs/nfs-pv.yaml
kubectl apply -f filesystem/nfs/nfs-pvc.yaml -n $NAMESPACE

# Verify NFS setup
# echo "Verifying NFS setup..."
# kubectl get pods -l app=nfs-server
# kubectl get pv
# kubectl get pvc

echo "Applying ZooKeeper StatefulSet..."
kubectl apply -f filesystem/zookeeper-statefulset.yaml -n $NAMESPACE

echo "Waiting for ZooKeeper to be ready..."
kubectl wait --for=condition=ready pod -l app=zookeeper --timeout=120s

# Verify ZooKeeper setup
# echo "Verifying ZooKeeper setup..."
# kubectl get pods -l app=zookeeper

echo "Setup complete. The following resources are available:"
# echo "NFS Server Pod:"
# kubectl get pods -l app=nfs-server
# echo "Persistent Volume:"
# kubectl get pv
# echo "Persistent Volume Claim:"
# kubectl get pvc
# echo "Zookeeper Pods:"
# kubectl get pods -l app=zookeeper

echo "To use the NFS storage, mount the PVC in your pods like this:"
echo "volumes:"
echo "  - name: nfs-storage"
echo "    persistentVolumeClaim:"
echo "      claimName: nfs-pvc"
echo "volumeMounts:"
echo "  - mountPath: /data"
echo "    name: nfs-storage"