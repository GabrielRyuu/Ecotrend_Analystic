import geopandas as gpd

def check_geojson():
    gdf = gpd.read_file("municipios_brasil.geojson", encoding='utf-8')
    
    print("Primeiras 10 cidades no arquivo GeoJSON:")
    print(gdf['name'].head(10))  
    
    print("\nColunas do arquivo GeoJSON:")
    print(gdf.columns)

if __name__ == "__main__":
    check_geojson()
