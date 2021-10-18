Work environment: VirtualBox
Working directory : Watcher
VM IP : 192.168.1.10
Storage Urls:
  
     - http://192.168.2.10:9000
        
     -  http://192.168.2.10:9002


Installation of Python environment on work_dir:

	sudo apt install python3-venv
	python3 -m venv venv
	. venv/bin/activate (ACTIVATE THE ENV)
   
Description:
   	
	Creation of a Minio Object storage instance along with its replica
   	Additional creation of  Watcher who is looking for notification  changes on  Minio storage  
   	Due to Watcher on  every upload/deletion of specific format files , relevant data modification is executed on replica
   
   	NOTE : Must specify on main.py Bucket,folder,file_format that Watcher will watch for on execution
   	e.g created on bucket 'goulibucket' , folder 'images' where Watcher is listening for files with 'jpeg' format

   	NOTE :  samples images for testing   on Watcher/minio/samples


   	NOTE : A  Stored Object is  automatically removed if is idle for > 30 sec 


