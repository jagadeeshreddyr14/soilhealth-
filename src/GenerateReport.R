options(echo = TRUE)
args <- commandArgs(trailingOnly = TRUE)
library(tibble)
library(knitr)
library(ini) 
library(httr)


data = read.ini('/home/satyukt/Projects/1000/soil_health/Config/config.ini', encoding = getOption("encoding"))


farm_name <- args[1]
fid <- unlist(strsplit(farm_name,'_'))[1]
crop <- args[2]
referal_code <- args[3]
lat <- args[4]
long <- args[5]



if (referal_code == '17684'){
    rmd.path <- file.path(data$default_report$home_path, data$default_report$kannda_rmd)
}else if (referal_code == '18913'){
    rmd.path <- file.path(data$default_report$home_path, data$hindi$hindi_rmd)
}else{
    rmd.path <- file.path(data$default_report$home_path, data$default_report$soil_rmd)
}
rmarkdown::render(rmd.path,
    params = list(args = fid, args1 = crop, args4 = lat, args5 = long),
    output_file = sprintf('%s%s%s.pdf',data$default_report$home_path, data$default_report$output_report,farm_name), clean = TRUE
)


log_file = file.path(data$default_report$home_path,data$default_report$rmd_log,paste0(farm_name, ".log"))
file.remove(log_file)
