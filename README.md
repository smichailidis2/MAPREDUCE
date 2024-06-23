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


To use Zookeeper for data synchronization use the following commands in the worker script:

-1 Connect to Zookeeper:
```python
from kazoo.client import KazooClient
zk = KazooClient(hosts='zookeeper:2181')
zk.start()
```

