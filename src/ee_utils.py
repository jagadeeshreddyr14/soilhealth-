


def maskS2clouds(image):
    '''
    image is the input extracted from sentinal-2 dataset 
    this function is to find whether image is covered with clouds and 
    to do this calculation we use QA60 image from sentinal-2 dataset 
    '''
    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
        qa.bitwiseAnd(cirrusBitMask).eq(0))

    return image.updateMask(mask).set("system:time_start", image.get("system:time_start"))
    
# def maskS2clouds_min_max(image):

#     qa = image.select('QA60')

#     cloudBitMask = 1 << 10
#     cirrusBitMask = 1 << 11

#     mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
#         qa.bitwiseAnd(cirrusBitMask).eq(0))

#     img = image.updateMask(mask).divide(10000)
#     img_time = img.set("system:time_start", image.get("system:time_start"))
#     return img_time


def addNDVI(image):
    '''
    this fuction is used to check whether the land is barren or not 
    ndvi is extracted using band B8 and B4 
    system:time_start is a property that when last time was passed 

    '''
    ndvi_s = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndvi = ndvi_s.set("system:time_start", image.get("system:time_start"))
    return image.addBands(ndvi)



def clipToCol(geometry):
    '''
    clip to geometry mentioned
    '''
    def climage(image):
        return image.clipToCollection(geometry)
    return climage



def masker(greenest, minest):
    '''
    here we are using decorator
    using ndvi to mask forest area nearer to farm region 
    '''
    def wrap(image):
            
        mask1 = greenest.select('NDVI').gt(0.3)
        mask2 = minest.select('NDVI').lt(0.6)
        mask3 = image.select('NDVI').gt(0.05)
        mask4 = image.select('NDVI').lt(0.3)
        return image.updateMask(mask1).updateMask(mask2).updateMask(mask3).updateMask(mask4)

    return wrap
