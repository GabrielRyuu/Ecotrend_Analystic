import ee

def calculate_sustainability_index(features, geometry):
    """
    Calcula o índice de sustentabilidade com base nas características extraídas.
    """
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
    
    sustainability_index = (ndvi_mean - ndbi_mean + 1) * 50  # Normaliza para 0-100
    return max(0, min(100, sustainability_index))  # Garante que o índice fique entre 0 e 100

def extract_city_data(features, geometry):
    """
    Extrai dados médios das características para uma cidade.
    """
    data = features.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        maxPixels=1e9
    ).getInfo()
    return data

