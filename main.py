from notifier import Watcher
from Slaves import Slave
Wclient=Watcher('10.10.2.51','9000','minio','minio123')
Wclient.Listen_bucket('goulibucket','images','.jpeg') # jpeg,jpg
