import geopandas as gpd
import logging
import ee
import time
from typing import Dict, Optional, Tuple, Any
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




@lru_cache(maxsize=32)
def get_city_geometry(city_name: str, geojson_file: str = "municipios_filtrados.geojson", buffer_meters: int = 10000) -> ee.Geometry:
    """Obtém a geometria de uma cidade com buffer personalizado.
    
    Args:
        buffer_meters: Raio do buffer em metros (padrão: 10km)
    """
    try:
        gdf = gpd.read_file(geojson_file)
        
        # Busca normalizada
        normalized_name = (city_name.lower()
                         .replace('ã', 'a')
                         .replace('á', 'a')
                         .replace('é', 'e'))
        
        city_data = gdf[gdf['name'].str.lower().str.normalize('NFKD')
                                  .str.encode('ascii', errors='ignore')
                                  .str.decode('utf-8')
                                  .str.replace('ã', 'a')
                                  .eq(normalized_name)]
        
        if city_data.empty:
            raise ValueError(f"Cidade {city_name} não encontrada")
            
        geom = city_data.iloc[0].geometry
        
        if geom.geom_type == 'Point':
            point = ee.Geometry.Point([geom.x, geom.y])
            return point.buffer(buffer_meters)  # Buffer circular
            
        raise ValueError(f"Tipo de geometria não suportado: {geom.geom_type}")
        
    except Exception as e:
        logger.error(f"Erro na geometria de {city_name}: {str(e)}")
        raise

def validate_sentinel_image(image: ee.Image, required_bands: list = None) -> bool:
    """Valida se uma imagem do Sentinel-2 contém todas as bandas necessárias.
    
    Args:
        image: Imagem do Earth Engine a ser validada
        required_bands: Lista de bandas obrigatórias
        
    Returns:
        True se a imagem for válida, False caso contrário
    """
    required_bands = required_bands or ['B2', 'B3', 'B4', 'B8', 'B11']
    available_bands = image.bandNames().getInfo()
    return all(b in available_bands for b in required_bands)

def get_satellite_images(geometry: ee.Geometry, 
                        start_date: str, 
                        end_date: str, 
                        max_cloud_cover: int = 20,
                        max_attempts: int = 3) -> ee.Image:
    """Obtém imagens do Sentinel-2 para a área e período especificados.
    
    Args:
        geometry: Geometria da área de interesse
        start_date: Data inicial no formato 'YYYY-MM-DD'
        end_date: Data final no formato 'YYYY-MM-DD'
        max_cloud_cover: Percentual máximo de cobertura de nuvens
        max_attempts: Número máximo de tentativas
        
    Returns:
        Imagem do Sentinel-2 processada
        
    Raises:
        ValueError: Se não encontrar imagens válidas
    """
    for attempt in range(max_attempts):
        try:
            collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                         .filterBounds(geometry)
                         .filterDate(start_date, end_date)
                         .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover)))
            
            if collection.size().getInfo() == 0:
                raise ValueError("Nenhuma imagem disponível para o período e localização")
                
            image = collection.median()
            
            if not validate_sentinel_image(image):
                raise ValueError("Imagem não contém todas as bandas necessárias")
                
            logger.info("Imagem do Sentinel-2 validada com sucesso")
            return image
            
        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}")
            if attempt == max_attempts - 1:
                raise
            time.sleep(5)

def calculate_vegetation_indices(image: ee.Image) -> ee.Image:
    """Calcula índices de vegetação (NDVI, NDBI, MNDWI) a partir de uma imagem.
    
    Args:
        image: Imagem do Sentinel-2
        
    Returns:
        Imagem com bandas adicionais dos índices calculados
        
    Raises:
        RuntimeError: Se ocorrer erro no cálculo dos índices
    """
    try:
        # NDVI - Índice de Vegetação (B8=NIR, B4=Red)
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        
        # NDBI - Índice de Áreas Construídas (B11=SWIR, B8=NIR)
        ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
        
        # MNDWI - Índice de Água (B3=Green, B11=SWIR)
        mndwi = image.normalizedDifference(['B3', 'B11']).rename('MNDWI')
        
        return image.addBands([ndvi, ndbi, mndwi])
        
    except Exception as e:
        logger.error(f"Erro no cálculo de índices: {str(e)}")
        raise

def extract_features(image: ee.Image, 
                    geometry: ee.Geometry,
                    scale: int = 100,
                    max_pixels: int = 1e9) -> Dict[str, float]:
    """Extrai características (features) de uma imagem para cálculo do índice.
    
    Args:
        image: Imagem do Sentinel-2 com bandas adicionais
        geometry: Geometria da área de interesse
        scale: Resolução espacial em metros
        max_pixels: Número máximo de pixels para processamento
        
    Returns:
        Dicionário com médias dos índices calculados
        
    Raises:
        RuntimeError: Se ocorrer erro na extração de features
    """
    try:
        # Calcular os índices de vegetação
        with_indices = calculate_vegetation_indices(image)
        
        # Extrair estatísticas
        stats = with_indices.select(['NDVI', 'NDBI', 'MNDWI']).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=scale,
            maxPixels=max_pixels
        ).getInfo()
        
        return {
            'NDVI_mean': stats.get('NDVI', 0),
            'NDBI_mean': stats.get('NDBI', 0),
            'MNDWI_mean': stats.get('MNDWI', 0)
        }
        
    except Exception as e:
        logger.error(f"Erro na extração de características: {str(e)}")
        raise
