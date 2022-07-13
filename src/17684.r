options(echo = TRUE)
args <- commandArgs(trailingOnly = TRUE)

library(knitr)
library(sf)
library(raster)
library(webshot)
library(htmlwidgets)
library(tmap)
library(rgeos)
library(leaflet)


# farm_name <- "2540"
farm_name <- args[1]
# farm_name <- "1052"
#### Farm Boundary ####
# dir_file <- "/home/satyukt/Projects/1000/area"

# in.glob <- Sys.glob(file.path(dir_file, farm_name))
# wkt <- read.table(sprintf("%s/%s.csv", dir_file, farm_name), header = FALSE, sep = "\t", stringsAsFactors = FALSE)
# shp_poly <- readWKT(wkt$V1)
# crs(shp_poly) <- "+proj=longlat +datum=WGS84 +no_defs"
# shp_file <- st_as_sfc(shp_poly)

# tmap_mode("view")
# map <- tm_basemap("Esri.WorldImagery") +
#     tm_shape(shp_file) + tm_polygons(alpha = 0, border.col = "red", lwd = 4) + tmap_options(check.and.fix = TRUE)


# lf <- tmap_leaflet(map)
# ## save html to png
# saveWidget(lf, "/home/satyukt/Projects/1000/temp.html", selfcontained = FALSE)
# webshot("/home/satyukt/Projects/1000/temp.html",
#     file = sprintf("/home/satyukt/Projects/1000/soil_health/output/Farm Boundary/%s/%s.png", farm_name, farm_name),
#     cliprect = "viewport"
# )




# Rmarkdown path
rmd.path <- "/home/satyukt/Projects/1000/soil_health/src/client_17684.Rmd"

# This will render the Rmd and Create the PDF for the Farm
rmarkdown::render(rmd.path,
    params = list(args = farm_name),
    output_file = paste0("/home/satyukt/Projects/1000/soil_health/output/Report/", farm_name, ".pdf"), clean = TRUE
)

file.remove(from = paste0("/home/satyukt/Projects/1000/soil_health/src/", farm_name, ".log"))
