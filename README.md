# MAPREDUCE - FileSystem Implementation

To use NFS storage, mount the PVC in your pods like this:


```yaml
spec:
    volumes:
    - name: nfs-storage
        persistentVolumeClaim:
        claimName: nfs-pvc
    volumeMounts:
    - mountPath: /data
        name: nfs-storage
```