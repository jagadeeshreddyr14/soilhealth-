
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
 

