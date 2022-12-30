options(echo = TRUE)
args <- commandArgs(trailingOnly = TRUE)
library(tibble)
library(knitr)
library(ini) 
library(httr)


data = read.ini('/home/satyukt/Projects/1000/soil_health/Config/config.ini', encoding = getOption("encoding"))


fid <- args[1]
crop <- args[2]
referal_code <- args[3]

lat <- args[4]
long <- args[5]
lang <- args[6]


if ((referal_code == '17684') & (tolower(crop)=='sugarcane')) {
    rmd.path <- file.path(data$default_report$home_path, data$kannda_rmd$sugarcane)
}else if (lang == 'hi'){
    rmd.path <- file.path(data$default_report$home_path, data$hindi$hindi_rmd)
}else if (lang == 'mr'){
    rmd.path <- file.path(data$default_report$home_path, data$marathi$marathi_rmd)
}else if (lang == 'te'){
    rmd.path <- file.path(data$default_report$home_path, data$telugu$telugu_rmd)
}else if (lang == 'gu'){
    rmd.path <- file.path(data$default_report$home_path, data$gujarati$gujarati_rmd)
}else{
    rmd.path <- file.path(data$default_report$home_path, data$default_report$soil_rmd)
}
rmarkdown::render(rmd.path,
    params = list(args = fid, args1 = crop, args4 = lat, args5 = long),
    output_file = sprintf('%s%s%s.pdf',data$default_report$home_path, data$default_report$output_report,fid), clean = TRUE
)


log_file = file.path(data$default_report$home_path,data$default_report$rmd_log,paste0(fid, ".log"))
file.remove(log_file)
