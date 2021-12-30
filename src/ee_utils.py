
def maskS2clouds(image):

    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
        qa.bitwiseAnd(cirrusBitMask).eq(0))

    return image.updateMask(mask)
    
def maskS2clouds_min_max(image):

    qa = image.select('QA60')

    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11

    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
        qa.bitwiseAnd(cirrusBitMask).eq(0))

    img = image.updateMask(mask).divide(10000)
    img_time = img.set("system:time_start", image.get("system:time_start"))
    return img_time


def addNDVI(image):
    ndvi_s = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndvi = ndvi_s.set("system:time_start", image.get("system:time_start"))
    return image.addBands(ndvi)



def clipToCol(geometry):
    def climage(image):
        return image.clipToCollection(geometry)
    return climage
