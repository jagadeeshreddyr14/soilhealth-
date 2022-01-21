
def maskS2clouds(image):

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
    ndvi_s = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndvi = ndvi_s.set("system:time_start", image.get("system:time_start"))
    return image.addBands(ndvi)



def clipToCol(geometry):
    def climage(image):
        return image.clipToCollection(geometry)
    return climage



def masker(greenest, minest):
    def wrap(image):
            
        mask1 = greenest.select('NDVI').gt(0.3)
        mask2 = minest.select('NDVI').lt(0.6)
        mask3 = image.select('NDVI').gt(0.05)
        mask4 = image.select('NDVI').lt(0.3)
        return image.updateMask(mask1).updateMask(mask2).updateMask(mask3).updateMask(mask4)

    return wrap
