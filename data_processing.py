import ee
import logging
from typing import Dict, Optional, Tuple
import numpy as np

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_sustainability_index(features: Dict[str, float], 
                                geometry: ee.Geometry,
                                weights: Dict[str, float] = None,
                                min_score: float = 0,
                                max_score: float = 100) -> Optional[float]:
    """Calcula o índice de sustentabilidade com base nos features extraídos.
    
    Args:
        features: Dicionário contendo NDVI_mean, NDBI_mean e MNDWI_mean
        geometry: Geometria da área analisada (para logs)
        weights: Pesos para cada feature (padrão: NDVI:0.4, MNDWI:0.3, NDBI:-0.2)
        min_score: Valor mínimo do índice
        max_score: Valor máximo do índice
        
    Returns:
        Índice de sustentabilidade normalizado ou None em caso de erro
    """
    try:
        # Validação dos inputs
        if not features or None in features.values():
            logger.warning("Features ausentes ou inválidos")
            return None
            
        # Pesos padrão
        default_weights = {
            'NDVI_mean': 0.4,  # Vegetação - impacto positivo
            'MNDWI_mean': 0.3,  # Água - impacto positivo
            'NDBI_mean': -0.2   # Área construída - impacto negativo
        }
        weights = weights or default_weights
        
        # Verifica features necessários
        required_features = ['NDVI_mean', 'NDBI_mean', 'MNDWI_mean']
        for feat in required_features:
            if feat not in features:
                raise ValueError(f"Feature {feat} não encontrado")
        
        # Cálculo do score ponderado
        score = sum(features[feat] * weights.get(feat, 0) for feat in required_features)
        
        # Normalização para a escala desejada
        normalized_score = np.interp(score, [-1, 1], [min_score, max_score])
        
        logger.debug(f"Cálculo de índice para {geometry.getInfo()}: "
                    f"NDVI={features['NDVI_mean']:.3f}, "
                    f"MNDWI={features['MNDWI_mean']:.3f}, "
                    f"NDBI={features['NDBI_mean']:.3f} → "
                    f"Score={normalized_score:.2f}")
        
        return round(normalized_score, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular índice para {geometry.getInfo()}: {str(e)}")
        return None
def extract_features(image: ee.Image, geometry: ee.Geometry) -> Dict[str, float]:
    """Versão robusta com fallbacks."""
    try:
        # Cálculo dos índices com verificação
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
        mndwi = image.normalizedDifference(['B3', 'B11']).rename('MNDWI')
        
        # Extração com fallback
        stats = ee.Image.cat([ndvi, ndbi, mndwi]).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=100,
            bestEffort=True,
            maxPixels=1e9
        ).getInfo()
        
        return {
            'NDVI_mean': stats.get('NDVI', 0.1) or 0.1,  # Valor mínimo razoável
            'NDBI_mean': stats.get('NDBI', 0),
            'MNDWI_mean': stats.get('MNDWI', 0)
        }
        
    except Exception as e:
        logger.error(f"Fallback para {geometry.getInfo()}: {str(e)}")
        return {'NDVI_mean': 0.1, 'NDBI_mean': 0, 'MNDWI_mean': 0}
