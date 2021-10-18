from minio import Minio 
from minio.deleteobjects import DeleteObject
from minio.error import InvalidResponseError 
from Slaves import Slave
import os
import time

# ,InvalidArgument

class Watcher:


        def __init__(self,host,port,access,secret):
                self.host=host
                self.port=port
                self.access=access
                self.secret=secret
                self.bucket='' # init bucket,prefix,suffix gonna use them later in listen_bucket
                self.prefix=''
                self.suffix=''



        def Get_addr(self): # returns full address
                return self.host + ':' + self.port

        def Create_Watcher(self,addr): # creates main watcher and his slaves
                Client=Slave('10.10.2.52','9002','minio2','minio456')
                Slave_s1=Client.Create()

                return Minio(addr,self.access,self.secret,secure=False),Slave_s1 # main watcher,slave

        def Listen_bucket(self,bucket,prefix,suffix): # callable func for main
                self.bucket=bucket
                self.prefix=prefix
                self.suffix=suffix
                watch,slave,events=self.EventMaker() # return event generator with watcher and his slaves
                self.Catch_Events(watch,slave,events) # Listening to events

        def EventMaker(self): # returns main watcher and his slaves with an event generator
                watch,slave = self.Create_Watcher(self.Get_addr()) # main watcher and his slaves
                events=watch.listen_bucket_notification(self.bucket,self.prefix,self.suffix,['s3:ObjectCreated:*','s3:ObjectRemoved:*','s3:ObjectAccessed:*'])
                print(events)
                return watch,slave,events


        def Get_Records(self,event):
                Records=event['Records']
                Event =Records[0]['eventName']
                Bucket = Records[0]['s3']['bucket']['name']
                file=Records[0]['s3']['object']['key']

                Splitter=file.split('/') # split eg test%2FServers.txt to get tes,Servers.txt
                Folder = Splitter[0]
                print('folder in split is: ',Folder)
                Obj = Splitter[1]

                print('Event: ',Event)
                print('Bucket: ',Bucket)
                print('File :', Folder)
                print('Object :', Obj)

                _,mysuffix = Obj.split('.') # split eg Servers.txt to get only .txt
                mysuffix = '.' + mysuffix

                if Bucket == self.bucket and mysuffix == self.suffix: # check if event bucket,suffix match with given
                        return Event,Folder + '/' + Obj
                else:
                        print('Something went  Wrong. Crashing...')
        def Download(self,Master,Dir):
                print("Retrieve Object...")
                print("Object to be retrieved: ",Dir)
                Master.fget_object(self.bucket,Dir,Dir) # makes inf loop because reads it as event
                print("Object downloaded succesfully")


        def Upload(self,Slave,Dir):
                print("Copying to slave server...")

                try:
                        with open(Dir, 'rb') as file_data:
                                file_stat = os.stat(Dir)
                                Slave.put_object(self.bucket, Dir,
                                        file_data, file_stat.st_size)
                except InvalidResponseError as err:
                        print(err)


        def Catch_Events(self,watch,slave,events):

                check = 0
                checkPUT=False #
                checkDEL=False
                
                start = time.time()
                print('Init timer at : %.2f' %  start)
                stamp = [] # init timestamps for used objects in bucket
                saved = [] # saved objects in bucket
                to_delete=[]



                

                curr = watch.list_objects(self.bucket,self.prefix,recursive = True)
                for el in curr :
                    saved.append(el.object_name)
                    stamp.append(start)
                print('Init saved objects in {} : \n {}'.format(self.bucket,saved))
                for el in events:

                        Event,Dir= self.Get_Records(el) # get records whenever a event occurs
                      
                        ########time deletion######
                        if check == 2 :
                            to_delete = []
                            timecheck = time.time()
                            for s,t in zip(saved,stamp):
                                
                                print('idle object ',s,' for: ',timecheck - t,'\n') # dir object so small cause stamp is being fixed at check == 0 maybe doesn't bother us

                                if timecheck - t >= 30 and s!= Dir: # if objs in server exceeds 30 s unused delete them for now dont consider used object idle(-ation) 
                                    to_delete.append(DeleteObject(s))
                                    #del stamp[saved.index(s)]
                                    #del saved[saved.index(s)]


                            print('To_delete :', to_delete,'\n')
                            for del_obj in watch.remove_objects(self.bucket,to_delete):

                                print('Timeout for ',del_obj)
                            print('\n')



                        ########time deletion######







                        if Event == 's3:ObjectCreated:Put':
                            check = 0 # Init check for event method Put event follows Head Event and Get Event
                            checkPUT = True
                        elif Event ==  's3:ObjectRemoved:Delete':
                            checkDEL = True


                        
                        
                        if (Event == 's3:ObjectAccessed:Get' or   Event == 's3:ObjectAccessed:Head') and check<=2:
                                if check == 2:
                                        checkPUT == False
                                        check = 0
                                        continue



                        notify=True

                        if notify == True:    # must see if the bucket exists in the other server
                            
                            if slave.bucket_exists(self.bucket) == True:
                                    print("Great success!!")
                            else:
                                    print("Faiiiiiiil")
                                    slave.make_bucket(self.bucket)
                                    
                                    
                        if checkDEL == True :
                            print('Deleting...')
                            slave.remove_object(self.bucket,Dir)
                            checkDEL = False
                            del stamp[saved.index(Dir)] # delete additionally from storage
                            del saved[saved.index(Dir)]

                            print('Complete')

            
                        if check == 0  and checkPUT == True:

                                self.Download(watch,Dir) # Download object to local filesystem to upload it to slave

                        if check == 1 and checkPUT == True:
                                self.Upload(slave,Dir) # upload object to slave server
                                checkPUT = False

                                if Dir not in saved : # if object first time used save it else change its stamp
                                    saved.append(Dir) # save used object
                                    stamp.append(time.time()) # save additional timestamp
                                    print('################################ \n')
                                    print('Save obj {}'.format(saved[saved.index(Dir)]),'at %.2f' % stamp[saved.index(Dir)],'\n')
                                    print('################################ \n')

                                else:
                                    pos = saved.index(Dir)
                                    stamp[pos] = time.time()
                                    print('################################ \n')

                                    print(' obj last time used {}'.format(saved[saved.index(Dir)]),'at %.2f' % stamp[saved.index(Dir)],'\n')
                                    print('################################ \n')
                                   

                                print('Complete')
                        check = check + 1
