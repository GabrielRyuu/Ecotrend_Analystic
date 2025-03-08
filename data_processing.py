import ee
import json

def calculate_sustainability_index(features, geometry, scale=10, max_pixels=1e9):
    """
    Calcula o Índice de Sustentabilidade com base no NDVI e NDBI médios em uma geometria.

    Parâmetros:
        features (ee.Image): Imagem contendo as bandas NDVI e NDBI.
        geometry (ee.Geometry): Geometria da área de interesse.
        scale (int): Resolução espacial em metros (padrão: 10).
        max_pixels (int): Número máximo de pixels permitidos para a operação (padrão: 1e9).

    Retorna:
        float: Índice de Sustentabilidade (0 a 100).
    """
    try:
        # Calcula a média do NDVI
        ndvi_mean = features.select('NDVI').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=scale,
            maxPixels=max_pixels
        ).getInfo().get('NDVI', 0)  # Retorna 0 se 'NDVI' não estiver disponível
        
        # Calcula a média do NDBI
        ndbi_mean = features.select('NDBI').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=scale,
            maxPixels=max_pixels
        ).getInfo().get('NDBI', 0)  # Retorna 0 se 'NDBI' não estiver disponível
        
        # Calcula o Índice de Sustentabilidade
        sustainability_index = (ndvi_mean - ndbi_mean + 1) * 50
        return max(0, min(100, sustainability_index))  # Garante que o índice esteja entre 0 e 100
    
    except Exception as e:
        print(f"Erro ao calcular o Índice de Sustentabilidade: {e}")
        return None


def extract_city_data(features, geometry, scale=10, max_pixels=1e9):
    """
    Extrai dados médios das bandas em uma geometria específica.

    Parâmetros:
        features (ee.Image): Imagem contendo as bandas desejadas.
        geometry (ee.Geometry): Geometria da área de interesse.
        scale (int): Resolução espacial em metros (padrão: 10).
        max_pixels (int): Número máximo de pixels permitidos para a operação (padrão: 1e9).

    Retorna:
        dict: Dados médios das bandas na geometria.
    """
    try:
        data = features.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=scale,
            maxPixels=max_pixels
        ).getInfo()
        
        return data if data else {}
    
    except Exception as e:
        print(f"Erro ao extrair dados da cidade: {e}")
        return {}


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
        return evi
    except Exception as e:
        print(f"Erro ao calcular EVI: {e}")
        return None


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
        return mndwi
    except Exception as e:
        print(f"Erro ao calcular MNDWI: {e}")
        return None


def calculate_statistics(features, geometry, scale=10, max_pixels=1e9):
    """
    Calcula estatísticas adicionais para as bandas selecionadas.

    Parâmetros:
        features (ee.Image): Imagem contendo as bandas desejadas.
        geometry (ee.Geometry): Geometria da área de interesse.
        scale (int): Resolução espacial em metros.
        max_pixels (int): Número máximo de pixels permitidos para a operação.

    Retorna:
        dict: Estatísticas adicionais das bandas na geometria.
    """
    try:
        stats = features.reduceRegion(
            reducer=ee.Reducer.mean()
            .combine(reducer2=ee.Reducer.median(), sharedInputs=True)
            .combine(reducer2=ee.Reducer.stdDev(), sharedInputs=True)
            .combine(reducer2=ee.Reducer.minMax(), sharedInputs=True),
            geometry=geometry,
            scale=scale,
            maxPixels=max_pixels
        ).getInfo()
        
        return stats if stats else {}
    
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        return {}


def normalize_data(value, min_value, max_value):
    """
    Normaliza um valor entre 0 e 1 com base no intervalo fornecido.

    Parâmetros:
        value (float): Valor a ser normalizado.
        min_value (float): Valor mínimo do intervalo.
        max_value (float): Valor máximo do intervalo.

    Retorna:
        float: Valor normalizado entre 0 e 1.
    """
    try:
        if max_value - min_value == 0:
            return 0
        return (value - min_value) / (max_value - min_value)
    except Exception as e:
        print(f"Erro ao normalizar dados: {e}")
        return None


def export_statistics_to_json(stats, filename="estatisticas.json"):
    """
    Exporta estatísticas calculadas para um arquivo JSON.

    Parâmetros:
        stats (dict): Estatísticas calculadas.
        filename (str): Nome do arquivo JSON gerado.

    Retorna:
        None
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(stats, file, indent=4)
        print(f"Estatísticas exportadas para {filename}")
    except Exception as e:
        print(f"Erro ao exportar estatísticas para JSON: {e}")

