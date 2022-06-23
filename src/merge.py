# import os
import subprocess
import time
import os
from subprocess import call,Popen,PIPE
import atexit
# your code here    
# path = 'E:/Satyukt/knitr/lucknow/csvs'
# dir_list = os.listdir(path)

args = ['30287']

for i in args:
#   start = time.time()
  # retcode = subprocess.call(['/usr/bin/R', '/home/satyukt/Projects/1000/soil_health/src/new_script.r',i])
#   print(time.time() - start)
  proc = Popen(["R --vanilla --args < /home/satyukt/Projects/1000/soil_health/src/new_script.r %s" %(i)], shell=True,stdout=PIPE)
  proc.communicate()
  atexit.register(proc.terminate)
  pid = proc.pid
# retcode = subprocess.call(['/usr/bin/R', '/home/satyukt/Projects/1000/soil_health/src/new_script.r','30287' ])
