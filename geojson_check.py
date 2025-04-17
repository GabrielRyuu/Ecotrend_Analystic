import geopandas as gpd
import folium

def check_geojson():
    # Carrega o arquivo GeoJSON
    try:
        gdf = gpd.read_file("municipios_filtrados.geojson", encoding='utf-8')
    except Exception as e:
        print(f"Erro ao carregar o arquivo GeoJSON: {e}")
        return None

    # Verifica se há coordenadas inválidas (NaN ou None)
    invalid_coords = gdf[gdf['geometry'].isna()]
    
    if not invalid_coords.empty:
        print("\nCidades com coordenadas inválidas (NaN):")
        print(invalid_coords[['name', 'geometry']])

        # Remover as cidades com coordenadas inválidas (ou preencher com valores padrões, se necessário)
        gdf = gdf.dropna(subset=['geometry'])  # Exemplo de remoção
        # Alternativamente, você pode atribuir coordenadas padrão
        # gdf.loc[gdf['geometry'].isna(), 'geometry'] = Point(-47.9292, -15.7801)  # Exemplo com ponto fixo
        
    else:
        print("\nNenhuma cidade com coordenadas inválidas.")

    return gdf

def create_interactive_map(gdf):
    # Cria o mapa
    mapa = folium.Map(location=[-15.7801, -47.9292], zoom_start=12)  # Posição inicial no Brasil
    
    # Marca as cidades no mapa
    for _, row in gdf.iterrows():
        # Verifica se a geometria é válida (sem valores nulos)
        if row['geometry'] and row['geometry'].is_valid:
            coords = row['geometry'].centroid.coords[:]
            longitude, latitude = coords[0]

            # Verifica se as coordenadas são válidas
            if longitude is not None and latitude is not None:
                folium.Marker(
                    location=[latitude, longitude],
                    popup=f"<b>{row['name']}</b>",
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(mapa)
        else:
            print(f"Cidade {row['name']} com geometria inválida ou sem coordenadas válidas.")
    
    return mapa

if __name__ == "__main__":
    # Verifica e ajusta o GeoDataFrame
    gdf = check_geojson()
    
    if gdf is not None:
        # Cria o mapa interativo
        mapa = create_interactive_map(gdf)
        
        # Salva o mapa em um arquivo HTML
        mapa.save("mapa_sustentabilidade.html")
        print("\nMapa interativo gerado com sucesso!")
    else:
        print("\nFalha ao gerar o mapa devido a erro no arquivo GeoJSON.")
