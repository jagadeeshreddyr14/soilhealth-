options(echo=TRUE)
args <- commandArgs(trailingOnly=TRUE)

farm_name <- args[1]

#Rmarkdown path
rmd.path <- '/home/satyukt/Projects/1000/soil_health/src/soil_health.Rmd'

#This will render the Rmd and Create the PDF for the Farm
rmarkdown::render(rmd.path,params = list(args = farm_name),
output_file = paste0('/home/satyukt/Projects/1000/soil_health/output/Report/',farm_name,'.pdf'), clean = TRUE)
