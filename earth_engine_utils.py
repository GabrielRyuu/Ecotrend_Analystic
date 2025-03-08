import geopandas as gpd
import logging
import ee
from streamlit import image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']

def initialize_ee(project_id):
    """
    Inicializa o Google Earth Engine.
    
    Parâmetros:
        project_id (str): ID do projeto no Google Cloud.
    """
    try:
        ee.Authenticate()
        ee.Initialize(project=project_id)
        logger.info(f"Earth Engine inicializado com o projeto: {project_id}")
    except Exception as e:
        logger.error(f"Erro ao inicializar o Earth Engine: {str(e)}")
        raise

def get_city_geometry(city_name, geojson_file="municipios_filtrados.geojson"):
    """
    Obtém a geometria (coordenadas) de uma cidade específica a partir do arquivo GeoJSON.
    
    Parâmetros:
        city_name (str): Nome da cidade.
        geojson_file (str): Nome do arquivo GeoJSON contendo os dados das cidades.
    
    Retorna:
        ee.Geometry.Point: Geometria da cidade no formato Earth Engine.
    """
    try:
        gdf = gpd.read_file(geojson_file)
        city_data = gdf[gdf['name'] == city_name]
        
        if city_data.empty:
            raise ValueError(f"Cidade {city_name} não encontrada no GeoJSON.")
        
        geometry = city_data.iloc[0].geometry
        logger.info(f"Geometria obtida para {city_name}.")
        
        return ee.Geometry.Point(geometry.x, geometry.y)
    except Exception as e:
        logger.error(f"Erro ao obter geometria para {city_name}: {str(e)}")
        raise

def get_satellite_images(geometry, start_date, end_date, max_cloud_cover=20):
    """
    Obtém imagens de satélite filtradas por data e cobertura de nuvens.
    
    Parâmetros:
        geometry (ee.Geometry): Geometria da área de interesse.
        start_date (str): Data inicial no formato 'YYYY-MM-DD'.
        end_date (str): Data final no formato 'YYYY-MM-DD'.
        max_cloud_cover (int): Porcentagem máxima de cobertura de nuvens permitida (padrão: 20).
    
    Retorna:
        ee.Image: Imagem composta (média) das imagens filtradas.
    """
    try:
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(geometry)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover))
        )
        logger.info(f"Imagens obtidas para a geometria especificada.")
        return collection.median()
    except Exception as e:
        logger.error(f"Erro ao obter imagens: {str(e)}")
        raise

def calculate_ndvi(image):
    """
    Calcula o NDVI (Índice de Vegetação por Diferença Normalizada).
    
    Parâmetros:
        image (ee.Image): Imagem contendo as bandas necessárias para o cálculo.
    
    Retorna:
        ee.Image: Imagem com a banda NDVI calculada.
    """
    try:
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        logger.info("NDVI calculado com sucesso.")
        return ndvi
    except Exception as e:
        logger.error(f"Erro ao calcular NDVI: {str(e)}")
        raise

def calculate_ndbi(image):
    """
    Calcula o NDBI (Índice de Áreas Construídas).
    
    Parâmetros:
        image (ee.Image): Imagem contendo as bandas necessárias para o cálculo.
    
    Retorna:
        ee.Image: Imagem com a banda NDBI calculada.
    """
    try:
        ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
        logger.info("NDBI calculado com sucesso.")
        return ndbi
    except Exception as e:
        logger.error(f"Erro ao calcular NDBI: {str(e)}")
        raise

def calculate_evi(image):
    """
    Calcula o EVI (Enhanced Vegetation Index).
    
    Parâmetros:
        image (ee.Image): Imagem contendo as bandas necessárias para o cálculo.
    
    Retorna:
        ee.Image: Imagem com a banda EVI calculada.
    """
    try:
        nir = image.select('B8')  # Near Infrared
        red = image.select('B4')  # Red
        blue = image.select('B2')  # Blue
        evi = nir.subtract(red).divide(nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)).multiply(2.5).rename('EVI')
        logger.info("EVI calculado com sucesso.")
        return evi
    except Exception as e:
        logger.error(f"Erro ao calcular EVI: {str(e)}")
        raise

def calculate_mndwi(image):
    """
    Calcula o MNDWI (Modified Normalized Difference Water Index).
    
    Parâmetros:
        image (ee.Image): Imagem contendo as bandas necessárias para o cálculo.
    
    Retorna:
        ee.Image: Imagem com a banda MNDWI calculada.
    """
    try:
        green = image.select('B3')  # Green
        swir = image.select('B11')  # Short Wave Infrared
        mndwi = green.subtract(swir).divide(green.add(swir)).rename('MNDWI')
        logger.info("MNDWI calculado com sucesso.")
        return mndwi
    except Exception as e:
        logger.error(f"Erro ao calcular MNDWI: {str(e)}")
        raise

def extract_features(image):
    """
    Extrai features como NDVI, NDBI, EVI e MNDWI da imagem fornecida.
    
    Parâmetros:
        image (ee.Image): Imagem contendo as bandas necessárias para os cálculos.
    
    Retorna:
        ee.Image: Imagem contendo todas as features adicionadas como bandas.
    """
    try:
        ndvi = calculate_ndvi(image)
        ndbi = calculate_ndbi(image)
        evi = calculate_evi(image)
        mndwi = calculate_mndwi(image)
        
        # Adiciona as bandas calculadas à imagem original
        features = image.addBands([ndvi, ndbi, evi, mndwi])
        
        logger.info("Features extraídas com sucesso.")
        return features
    except Exception as e:
        logger.error(f"Erro ao extrair features: {str(e)}")
        raise
