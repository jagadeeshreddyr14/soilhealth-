  # library(raster)
  # library(rgdal)
  # years <- Sys.glob('/home/satyukt/Projects/1000/soil_health/output/tif/1582/*.tif')
  # dist.file <- '/home/satyukt/Projects/1000/soil_health/output/tif/1582/1582.gpkg'
  # dist.ply <- readOGR(dist.file, stringsAsFactors = F)
  # crs.4326 <- '+proj=longlat +datum=WGS84 +no_defs'
  # dist.ply <- spTransform(dist.ply, CRS(crs.4326)) # Reproject to WGS 84 4326
  # out.dir <- "/home/satyukt/Projects/1000/soil_health/output/tif/1582/out/"
  # for(year in years){
  #   out.file <- file.path(out.dir, basename(year))
  #   
  #   
  #       r <- raster(year)
  #       r <- crop(r, dist.ply,snap ="out")
  #       r1 <- mask(r,dist.ply)
  #       #r3 <- resample(r, foo, na.rm = T)  
  #       #r[r > 1000] <- NA
  #       writeRaster(r1, out.file,overwrite=TRUE)
  #       print(out.file)     
  # }
  
  
  library(maptools)
  library(GISTools)
  library(raster)
  library(rgdal)
  library(sp)
  library(prettymapr)
  library(sf)
  library(png)
  library(naturalsort)
  fileName = "test_Siddappa"
  #in.files  = Sys.glob("/home/subash/Projects/1000/micro_v2/sm/out/*")
  in.files <-Sys.glob(sprintf("/home/satyukt/Projects/1000/soil_health/output/tif/%s", fileName))
  #farms.id = as.numeric(sapply(strsplit(basename(in.files), " "), "[[", 1))
  #farms.id = farms.id[!is.na(farms.id)]
  in.dir = "/home/satyukt/Projects/1000/soil_health/output/tif/"
  csv.dir = "/home/satyukt/Projects/1000/soil_health/output/client_wkt/"
  dir.out = "/home/satyukt/Projects/1000/soil_health/output/png/"
  col.pal <- colorRampPalette(c("#D7191C","#FDAE61","#FFFF00","#00FF00","#009CFF"))
  na.check = function(in.file){
    r.vals <- in.file[]
    u.val <- unique(r.vals)
    return(length(u.val))
  }
  plt.png = function(ras,out.file,date,shp.in,original_shp,name, count)
    if(!file.exists(out.file)){
      png(out.file)
      #dt = substr(basename(ras.file),1,15)
      #dt <- gsub("T.*",'',name)
      #pH [6,7.4]
      #P [25, 60]
      #OC [0.36, 0.6]
      #N [200, 320]
      #K [140, 260]
      #name="K"
      title = list('Potassium (kg/ha)', 'Nitrogen (kg/ha)','Organic Carban (%)','Phosphorus (kg/ha)','pH')
      lim = list("140, 260","200, 320","0.36, 0.6","25, 60","0.36, 0.6") # zlim=c(str(lim[1]))
      plot(ras,main=c(paste(" "),paste(title[count])),axes = FALSE, col = col.pal(255), par(bty = 'n'),xpd=TRUE)
      plot(shp.in,col="#FFFEFE",border="white",add=T)
      plot(original_shp,col='#00000000',border='black',add=T)
      dev.off()
      print(out.file)
    }
  
    farm.id <- fileName
    file.csv = sprintf("%s%s.csv",csv.dir,farm.id)
    if(file.exists(file.csv)){
      in.csv = read.csv(file.csv,header = F)
      cols = colnames(in.csv)
      in.csv$geometry <- do.call(paste, c(in.csv[cols], sep=","))
      for (co in cols) in.csv[co] <- NULL
      shp.in <-readWKT(in.csv)
      crs(shp.in)<-"+proj=longlat +datum=WGS84 +no_defs"
      shp_poly_sfc<-st_as_sfc(shp.in)
      ids = list("K","N","OC","P","pH")
      count <- 1
      for (id in ids) {
        print(id)
        #break
        ras.files = Sys.glob(sprintf("%s/%s/%s.tif",in.dir,farm.id,id))
        in.ras = raster(ras.files)
        
        #######################################
        shp_poly_sfc_proj<-st_transform(shp_poly_sfc,proj4string(in.ras))
        #######################################
        e<-extent(in.ras)
        extent_shp <- as(e, 'SpatialPolygons')
        proj4string(extent_shp) <- crs(in.ras)
        extent_shp<-st_as_sfc(st_bbox(extent_shp))
        extent_shp_proj<-st_transform(extent_shp,proj4string(in.ras))
        extent_shp_proj_buf <-st_buffer(extent_shp_proj, 20)
        ###################################################
        sf_use_s2(FALSE)
        cropped_shp<-st_difference(extent_shp_proj_buf,st_make_valid(shp_poly_sfc_proj))
        #dt = substr(basename(ras.file),1,3)
        dt <- gsub(".tif",'',basename(ras.files))
        date = as.Date(as.character(dt),format="%Y%m%d")
        date_text <- format(date, format = "%d %B %Y")
        in.ras<-projectRaster(in.ras,crs=st_crs(4326)$proj4string)
        cropped_shp=st_transform(cropped_shp,4326)
        na.file = na.check(in.ras)
        if(!na.file == 1){
          # Full and Partial (NA Free)
          out.png = sprintf("%s%s/",dir.out,farm.id)
          ifelse(!dir.exists(out.png), dir.create(out.png,recursive = TRUE), TRUE)
          out.file = sprintf("%s%s.png",sprintf("%s",out.png),dt)
          plt.png(in.ras,out.file,date_text,cropped_shp,shp_poly_sfc,dt, count)
        }
        count <- count + 1
        }
      break 
    }
   
    
