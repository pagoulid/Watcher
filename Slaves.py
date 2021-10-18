from minio import Minio
from minio.error import InvalidResponseError

class Slave:
        def __init__(self,host,port,access,secret):
                self.host=host
                self.port=port
                self.access=access
                self.secret=secret

        def Create(self): # create slaves
                if  (type(self.host)==type(self.port)): # types must match if 1 slave type=string else type=list of strings
                        if isinstance('str',type(self.host)) == True :
                                addr = self.host + ':' + self.port
                                print('address:',addr,'acc key:',self.access,'sec key',self.secret)

                                return Minio(addr,self.access,self.secret,secure=False)

                        elif isinstance('list',type(self.host))  == True:
                                Sl = []
                                for k in range(0,len(self.host)-1):
                                        addr = self.host[k] + ':' + self.port[k]
                                        Sl.append(Minio(addr,self.access[k],self.secret[k],secure=False))
                                return Sl
                        else:
                                print('something wrong')
                else:
                        print('Fail')
