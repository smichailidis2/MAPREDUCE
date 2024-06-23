#!/bin/bash

# Delete GlusterFS StatefulSet, service, and PVC if they exist
echo "Deleting GlusterFS StatefulSet, service, and PVC if they exist..."
kubectl delete statefulset glusterfs --ignore-not-found=true
kubectl delete service glusterfs --ignore-not-found=true
kubectl delete pvc glusterfs-pvc --ignore-not-found=true
kubectl delete pv glusterfs-pv --ignore-not-found=true

# Delete existing NFS resources if they exist
echo "Deleting existing NFS resources if they exist..."
kubectl delete deployment nfs-server --ignore-not-found=true
kubectl delete service nfs-server --ignore-not-found=true
kubectl delete pvc nfs-pvc --ignore-not-found=true
kubectl delete pv nfs-pv --ignore-not-found=true

# Apply NFS server service and deployment
echo "Applying NFS server service and deployment..."
kubectl apply -f nfs/nfs-service.yaml
kubectl apply -f nfs/nfs-deployment.yaml

# Wait for NFS server to be ready
echo "Waiting for NFS server to be ready..."
kubectl wait --for=condition=ready pod -l app=nfs-server --timeout=120s

# Apply Persistent Volume and Persistent Volume Claim
echo "Applying Persistent Volume and Persistent Volume Claim..."
kubectl apply -f nfs/nfs-pv.yaml
kubectl apply -f nfs/nfs-pvc.yaml

# Verify NFS setup
echo "Verifying NFS setup..."
kubectl get pods -l app=nfs-server
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
echo "NFS Server Pod:"
kubectl get pods -l app=nfs-server
echo "Persistent Volume:"
kubectl get pv
echo "Persistent Volume Claim:"
kubectl get pvc
echo "Zookeeper Pods:"
kubectl get pods -l app=zookeeper

echo "To use the NFS storage, mount the PVC in your pods like this:"
echo "volumes:"
echo "  - name: nfs-storage"
echo "    persistentVolumeClaim:"
echo "      claimName: nfs-pvc"
echo "volumeMounts:"
echo "  - mountPath: /data"
echo "    name: nfs-storage"
