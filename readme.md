
# How to predict the Model

Derive  'B8', 'B4', 'B5', 'B11','B9', 'B1', 'SR_n2', 'SR_N', 'TBVI1', 'NDWI', 'NDVI_G' these indicies in the order which it is mentioned. 

`data` dir contains pickle files with models saved to it. 

`src` dir contains the source code for soil-health prediction 


How to run the repo

1. clone the repo

`git clone https://github.com/aman-satyukt/soil-health.git`

2. Run this command

`conda env create -f environment.txt`

3. Using pip

`python -m venv .`

`source venv/bin/activate`

`pip install -r environment.txt`


# Info on code and implementation

## - soil_health.py

1. Executable file which outputs tiff for now for the bounded box of the feature. Later plan to save the raster in memory and then output clipped to the feature. 
2. The output of the soil_health.py script is saved to `output` dir. it has `tif` folder and inside that each folder is named after the farm id. Inside that we have nutrient values for that farm. We could eliminate this step and save it in memory.

3. The zonal_stats script is imported and run to get a dict of the value of the farm.

4. If the farm has high vegetation, we cannot comute and thus have to find a date when vegetation is low. Also, mask it to know this occurs

