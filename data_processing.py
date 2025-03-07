import ee

def calculate_sustainability_index(features, geometry):
    ndvi_mean = features.select('NDVI').reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        maxPixels=1e9
    ).getInfo()['NDVI']
    
    ndbi_mean = features.select('NDBI').reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        maxPixels=1e9
    ).getInfo()['NDBI']
    
    sustainability_index = (ndvi_mean - ndbi_mean + 1) * 50  
    return max(0, min(100, sustainability_index))  

def extract_city_data(features, geometry):
    data = features.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        maxPixels=1e9
    ).getInfo()
    return data
