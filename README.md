# MAPREDUCE - FileSystem Implementation

volumes:
  - name: nfs-storage
    persistentVolumeClaim:
      claimName: nfs-pvc
volumeMounts:
  - mountPath: /data
    name: nfs-storage