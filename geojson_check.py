import geopandas as gpd

def check_geojson():
    """
    Verifica o conteúdo do arquivo GeoJSON para garantir que as cidades estão sendo lidas corretamente.
    """
    gdf = gpd.read_file("municipios_brasil.geojson", encoding='utf-8')
    
    # Listar as primeiras 10 cidades do arquivo
    print("Primeiras 10 cidades no arquivo GeoJSON:")
    print(gdf['name'].head(10))  # Substitua 'name' pelo nome da coluna que contém as cidades
    
    # Verificar as colunas do arquivo GeoJSON
    print("\nColunas do arquivo GeoJSON:")
    print(gdf.columns)

# Chame a função para fazer o diagnóstico
if __name__ == "__main__":
    check_geojson()
