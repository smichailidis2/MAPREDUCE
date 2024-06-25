#!/bin/bash

# Retrieve Minikube IP
MINIKUBE_IP=$(minikube ip)

# Create glusterfs-endpoints.yaml dynamically
cat <<EOF > glusterfs/glusterfs-endpoints.yaml
apiVersion: v1
kind: Endpoints
metadata:
  name: glusterfs-cluster
subsets:
  - addresses:
      - ip: $MINIKUBE_IP
    ports:
      - port: 24007
EOF

# Delete NFS StatefulSet, service, and PVC if they exist
echo "Deleting NFS StatefulSet, service, and PVC if they exist..."
kubectl delete statefulset nfs-server --ignore-not-found=true
kubectl delete service nfs-server --ignore-not-found=true
kubectl delete pvc nfs-pvc --ignore-not-found=true
kubectl delete pv nfs-pv --ignore-not-found=true

# Apply GlusterFS endpoints, service, and statefulset
echo "Applying GlusterFS endpoints, service, and statefulset..."
kubectl apply -f glusterfs/glusterfs-endpoints.yaml
kubectl apply -f glusterfs/glusterfs-service.yaml
kubectl apply -f glusterfs/glusterfs-statefulset.yaml

# Wait for GlusterFS to be ready
echo "Waiting for GlusterFS to be ready..."
kubectl wait --for=condition=ready pod -l app=glusterfs --timeout=120s

# Apply Persistent Volume and Persistent Volume Claim
echo "Applying Persistent Volume and Persistent Volume Claim..."
kubectl apply -f glusterfs/glusterfs-pv.yaml
kubectl apply -f glusterfs/glusterfs-pvc.yaml

# Verify GlusterFS setup
echo "Verifying GlusterFS setup..."
kubectl get pods -l app=glusterfs
kubectl get pv
kubectl get pvc

# Apply Zookeeper StatefulSet
echo "Applying Zookeeper StatefulSet..."
kubectl apply -f zookeeper-statefulset.yaml

# Wait for Zookeeper to be ready
echo "Waiting for Zookeeper to be ready..."
kubectl wait --for=condition=ready pod -l app=zookeeper --timeout=120s

# Verify Zookeeper setup
echo "Verifying Zookeeper setup..."
kubectl get pods -l app=zookeeper

echo "Setup complete. The following resources are available:"
echo "GlusterFS Pod:"
kubectl get pods -l app=glusterfs
echo "Persistent Volume:"
kubectl get pv
echo "Persistent Volume Claim:"
kubectl get pvc
echo "Zookeeper Pods:"
kubectl get pods -l app=zookeeper

echo "To use the GlusterFS storage, mount the PVC in your pods like this:"
echo "volumes:"
echo "  - name: glusterfs-storage"
echo "    persistentVolumeClaim:"
echo "      claimName: glusterfs-pvc"
echo "volumeMounts:"
echo "  - mountPath: /data"
echo "    name: glusterfs-storage"
