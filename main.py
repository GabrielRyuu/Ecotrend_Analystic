from earth_engine_utils import initialize_ee, get_city_geometry, get_satellite_images, extract_features
from data_processing import calculate_sustainability_index
from visualization import plot_sustainability_index, create_interactive_map
import os

CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']

def main():
    GEOJSON_FILE = "municipios_filtrados.geojson"
    
    if not os.path.exists(GEOJSON_FILE):
        from data_preparation import prepare_data
        prepare_data()

    initialize_ee(project_id='ee-shiryucode')  

    resultados = {}
    coordenadas = {}

    for cidade in CIDADES_ALVO:
        try:
            print(f"\nProcessando: {cidade}")
            
            geometry = get_city_geometry(cidade)
            
            imagem = get_satellite_images(
                geometry=geometry,
                start_date='2023-01-01',
                end_date='2023-12-31'
            )
            
            features = extract_features(imagem)
            
            indice = calculate_sustainability_index(features, geometry)
            resultados[cidade] = indice
            
            coords = geometry.coordinates().getInfo()
            coordenadas[cidade] = (coords[1], coords[0])  

        except Exception as e:
            print(f"Erro em {cidade}: {str(e)}")
            resultados[cidade] = None

    if resultados:
        print("\nResultados finais:")
        for cidade, indice in resultados.items():
            print(f"{cidade}: {indice:.2f}" if indice else f"{cidade}: N/A")

        plot_sustainability_index(resultados)
        
        mapa = create_interactive_map(coordenadas, resultados)
        mapa.save("mapa_sustentabilidade.html")
        print("\nMapa interativo gerado com sucesso!")

if __name__ == "__main__":
    main()
