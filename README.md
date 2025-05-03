# 🌱 EcoTrend Analystic – Índice de Sustentabilidade Urbana

EcoMap é uma aplicação interativa que avalia a sustentabilidade de grandes cidades brasileiras utilizando imagens de satélite, dados ambientais e indicadores socioeconômicos. Com base em índices como NDVI, NDBI, EVI e MNDWI processados pelo Google Earth Engine, o sistema calcula um **índice composto de sustentabilidade urbana** e apresenta os resultados de forma visual em um **mapa interativo** e **gráficos comparativos**.

## 📸 Imagens da Interface

### Mapa Interativo
![Mapa Interativo](images/mapa_sustentabilidade.png)

### Dashboard Streamlit
![Dashboard](images/dashboard.png)

---

## 📊 Funcionalidades

- 📍 Visualização do índice de sustentabilidade por cidade no mapa.
- 🛰️ Processamento de dados via Google Earth Engine (NDVI, NDBI, EVI, MNDWI).
- 📈 Gráficos comparativos entre sustentabilidade, IDH, área verde e temperatura.
- 📁 Exportação dos resultados para `.csv`.
- 🔎 Validação automática de coordenadas GeoJSON.
- 💡 Interface simples com Streamlit para análise e exploração.

---

## 📂 Estrutura do Projeto

EcoMap/
│
├── main.py # Script principal de processamento
├── dashboard.py # Interface com Streamlit
├── data_processing.py # Cálculo do índice de sustentabilidade
├── data_preparation.py # Pré-processamento de dados
├── earth_engine_utils.py # Conexão e operações com Google Earth Engine
├── geojson_check.py # Validação de coordenadas GeoJSON
├── visualization.py # Geração de gráficos
├── mapa_sustentabilidade.html # Mapa interativo com Leaflet
├── resultados_sustentabilidade.csv # Saída com dados finais
├── images/ # Imagens usadas no README
│ ├── mapa_sustentabilidade.png
│ └── dashboard.png



---

## ▶️ Como Executar

### 1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/ecomap.git
cd ecomap
2. Instale as dependências:
bash
Copiar
Editar
pip install -r requirements.txt
Certifique-se de ter o earthengine autenticado:

bash
Copiar
Editar
earthengine authenticate
3. Execute o processamento:
bash
Copiar
Editar
python main.py
4. Inicie a interface:
bash
Copiar
Editar
streamlit run dashboard.py
📥 Requisitos
Python 3.8+

Google Earth Engine (API)

Pandas, Numpy, Streamlit, Plotly

Acesso autorizado à conta do GEE

🧠 Como o Índice é Calculado?
O índice de sustentabilidade é uma média ponderada de variáveis obtidas por sensoriamento remoto:

NDVI – vegetação

NDBI – áreas construídas

EVI – vegetação aprimorada

MNDWI – cobertura hídrica

Esses valores são normalizados e combinados para gerar um valor único de 0 a 100 por cidade.

🔗 Links Úteis
Google Earth Engine

Streamlit

Documentação NDVI e índices

👨‍💻 Autor
Desenvolvido por [Gabriel Cortes Teixeira]
🔗 
