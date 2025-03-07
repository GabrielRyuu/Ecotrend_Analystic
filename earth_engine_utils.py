import geopandas as gpd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']

def initialize_ee(project_id):
    try:
        ee.Authenticate()
        ee.Initialize(project=project_id)
        logger.info(f"Earth Engine inicializado com o projeto: {project_id}")
    except Exception as e:
        logger.error(f"Erro ao inicializar o Earth Engine: {str(e)}")
        raise

def get_city_geometry(city_name):
    try:
        gdf = gpd.read_file("municipios_filtrados.geojson")
        city_data = gdf[gdf['name'] == city_name]
        
        if city_data.empty:
            raise ValueError(f"Cidade {city_name} não encontrada no GeoJSON")
        
        geometry = city_data.iloc[0].geometry
        logger.info(f"Geometria encontrada para {city_name}")
        
        return ee.Geometry.Point(geometry.x, geometry.y)
        
    except Exception as e:
        logger.error(f"Erro ao obter geometria para {city_name}: {str(e)}")
        raise

def get_satellite_images(geometry, start_date, end_date, max_cloud_cover=20):
    try:
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(geometry)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover))
        )
        logger.info(f"Imagens obtidas para {geometry.getInfo()}")
        return collection.median()
    except Exception as e:
        logger.error(f"Erro ao obter imagens: {str(e)}")
        raise

def calculate_ndvi(image):
    try:
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        logger.info("NDVI calculado com sucesso")
        return ndvi
    except Exception as e:
        logger.error(f"Erro no cálculo do NDVI: {str(e)}")
        raise

def calculate_ndbi(image):
    try:
        ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
        logger.info("NDBI calculado com sucesso")
        return ndbi
    except Exception as e:
        logger.error(f"Erro no cálculo do NDBI: {str(e)}")
        raise

def extract_features(image):
    try:
        ndvi = calculate_ndvi(image)
        ndbi = calculate_ndbi(image)
        features = image.addBands([ndvi, ndbi])
        logger.info("Features extraídas com sucesso")
        return features
    except Exception as e:
        logger.error(f"Erro na extração de features: {str(e)}")
        raise
