from earth_engine_utils import initialize_ee, get_city_geometry, get_satellite_images, extract_features
from data_processing import calculate_sustainability_index
from visualization import plot_sustainability_index, create_interactive_map
import os

# Lista definitiva de cidades para análise
CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']

def main():
    # 1. Configuração inicial
    GEOJSON_FILE = "municipios_filtrados.geojson"
    
    # 2. Verifica e prepara dados geográficos
    if not os.path.exists(GEOJSON_FILE):
        from data_preparation import prepare_data
        prepare_data()

    # 3. Inicialização do Earth Engine
    initialize_ee(project_id='ee-shiryucode')  # Substitua pelo seu projeto ID

    # 4. Processamento principal
    resultados = {}
    coordenadas = {}

    for cidade in CIDADES_ALVO:
        try:
            print(f"\nProcessando: {cidade}")
            
            # 4.1 Obter geometria
            geometry = get_city_geometry(cidade)
            
            # 4.2 Coletar imagens de satélite
            imagem = get_satellite_images(
                geometry=geometry,
                start_date='2023-01-01',
                end_date='2023-12-31'
            )
            
            # 4.3 Extrair características
            features = extract_features(imagem)
            
            # 4.4 Calcular índice
            indice = calculate_sustainability_index(features, geometry)
            resultados[cidade] = indice
            
            # 4.5 Armazenar coordenadas para visualização
            coords = geometry.coordinates().getInfo()
            coordenadas[cidade] = (coords[1], coords[0])  # (lat, lon)

        except Exception as e:
            print(f"Erro em {cidade}: {str(e)}")
            resultados[cidade] = None

    # 5. Visualização dos resultados
    if resultados:
        print("\nResultados finais:")
        for cidade, indice in resultados.items():
            print(f"{cidade}: {indice:.2f}" if indice else f"{cidade}: N/A")

        # 5.1 Plotar gráfico
        plot_sustainability_index(resultados)
        
        # 5.2 Gerar mapa interativo
        mapa = create_interactive_map(coordenadas, resultados)
        mapa.save("mapa_sustentabilidade.html")
        print("\nMapa interativo gerado com sucesso!")

if __name__ == "__main__":
    main()
