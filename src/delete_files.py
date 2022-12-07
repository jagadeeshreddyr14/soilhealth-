#!/usr/bin/env python
# coding: utf-8

# In[30]:


import os
import shutil


# In[60]:


def Delete_files(farm):
 

    try:
        csv_path = f"/home/satyukt/Projects/1000/soil_health/output/csv/{farm}.csv"
        
        os.remove(csv_path)
    except Exception as e:
        pass


    try:
        png_path = f"/home/satyukt/Projects/1000/soil_health/output/png/{farm}/"
        shutil.rmtree(png_path, ignore_errors=False)
    except Exception as e:
        pass

    try:
        report_path = f"/home/satyukt/Projects/1000/soil_health/output/Report/{farm}.pdf"
        os.remove(report_path)
    except Exception as e:
        pass

    try:
        tiff_path = f"/home/satyukt/Projects/1000/soil_health/output/tif/{farm}/"
        shutil.rmtree(tiff_path, ignore_errors=False)
    except Exception as e:
        pass 
        
if __name__ == "__main__":
    
    farms = [56651]
    Delete_files(farms)
         
   
    
    
    

