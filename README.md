# MAPREDUCE - FileSystem Implementation

To use NFS storage, mount the PVC in your pods like this:


```yaml
spec:
    volumes:
    - name: glusterfs-storage
        persistentVolumeClaim:
        claimName: glusterfs-pvc
    volumeMounts:
    - mountPath: /data
        name: glusterfs-storage
```


To use Zookeeper for data synchronization use the following commands in the worker script:

1. Connect to Zookeeper:
```python
from kazoo.client import KazooClient
zk = KazooClient(hosts='zookeeper-0.zookeeper,zookeeper-1.zookeeper,zookeeper-2.zookeeper:2181')
zk.start()
```
2. Create a ZNode:
```python
zk.create("/mapreduce", b"my_data", ephemeral=True, makepath=True)
```
3. Check if a ZNode Exists:
```python
if zk.exists("/mapreduce"):
    print("ZNode exists")
```
4. Get Data from a ZNode:
```python
data, stat = zk.get("/mapreduce")
print("Data: %s" % data.decode("utf-8"))
```
5. Set Data in a ZNode:
```python
zk.set("/mapreduce", b"new_data")
```
6. Watch for Changes on a ZNode:
```python
def watch_node(event):
    print("Data changed")
zk.DataWatch("/mapreduce", watch_node)
```
7. Delete a ZNode
```python
zk.delete("/mapreduce")
```
