'''
This file is used to extract the other bands/
using derived band
'''
def NDWI_function(image):
  NDWI = image.expression(
      '(B03-B08)/(B03+B08)', {
        'B03': image.select('B3'),
        'B08': image.select('B8')

  }).rename('NDWI')
  return image.addBands(NDWI)

    
def TBVI1_function(image):

  TBVI1 = image.expression(
    'B05/(B05+B02)', {
      'B02': image.select('B2'),
      'B05': image.select('B5')

  }).rename('TBVI1')
  return image.addBands(TBVI1)


    
def NDVI_G_function(image):

  NDVI_G = image.expression(
  '(B8A-B03)/(B8A+B03)', {
  'B03': image.select('B3'),
  'B8A': image.select('B8A')

  }).rename('NDVI_G')
  return image.addBands(NDVI_G)

    
def SR_N_function(image):
  SR_N = image.expression(
  'B8A/B02', {
  'B02': image.select('B2'),
  'B8A': image.select('B8A')

  }).rename('SR_N')
  return image.addBands(SR_N)

def SR_n2_function(image):
  SR_n2 = image.expression(
      'B08/B03', {
        'B03': image.select('B3'),
        'B08': image.select('B8')
  
  }).rename('SR_n2')
  return image.addBands(SR_n2)

def NDVI_function(image):

  NDVI = image.expression(
      '(B08-B04)/(B08+B04)', {
        'B04': image.select('B4'),
        'B08': image.select('B8')

  }).rename('NDVI')
  return image.addBands(NDVI)
