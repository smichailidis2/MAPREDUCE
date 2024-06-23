#filesystem-setup.sh
#!/bin/bash

# Apply NFS server deployment and service
echo "Applying NFS server deployment and service..."
kubectl apply -f nfs-server.yaml

# Wait for NFS server to be ready
echo "Waiting for NFS server to be ready..."
kubectl wait --for=condition=ready pod -l app=nfs-server --timeout=120s

# Apply Persistent Volume and Persistent Volume Claim
echo "Applying Persistent Volume and Persistent Volume Claim..."
kubectl apply -f nfs-pv.yaml
kubectl apply -f nfs-pvc.yaml

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
