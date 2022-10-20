options(echo = TRUE)
args <- commandArgs(trailingOnly = TRUE)

library(knitr)


# farm_name <- "2540"
farm_name <- args[1]
crop <- args[2]
referal_code <- args[3]


if (referal_code == '17684'){
    rmd.path <- "/home/satyukt/Projects/1000/soil_health/data/Report_data/RMD/client_17684.Rmd"
} else if (referal_code == '15368'){
    rmd.path <- "/home/satyukt/Projects/1000/soil_health/data/Report_data/RMD/client_15368.Rmd"
}else if (referal_code == 'kannada'){
    rmd.path <- "/home/satyukt/Projects/1000/soil_health/data/Report_data/RMD/kannda_rep.Rmd"
}else{
    rmd.path <- "/home/satyukt/Projects/1000/soil_health/data/Report_data/RMD/soil_health.Rmd"
}
# rmd.path <- "/home/satyukt/Projects/1000/soil_health/data/Report_data/RMD/soil_health.Rmd"


# Rmarkdown path
#rmd.path <- "/home/satyukt/Projects/1000/soil_health/src/soil_health.Rmd"

# This will render the Rmd and Create the PDF for the Farm
rmarkdown::render(rmd.path,
    params = list(args = farm_name, args1 = crop),
    output_file = paste0("/home/satyukt/Projects/1000/soil_health/output/Report/", farm_name, ".pdf"), clean = TRUE
)

file.remove(from = paste0("/home/satyukt/Projects/1000/soil_health/data/Report_data/RMD/", farm_name, ".log"))



