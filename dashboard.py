import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from visualization import plot_comparacao_idh_area_verde, plot_radar

# Dados simulados (substitua pelos resultados reais do seu projeto)
indices = {
    'São Paulo': 76,
    'Rio de Janeiro': 82,
    'Belo Horizonte': 64,
    'Brasília': 93,
    'Salvador': 58
}

# Dados das cidades e suas coordenadas
coordenadas_cidades = {
    'São Paulo': [-23.55052, -46.633308],
    'Rio de Janeiro': [-22.906847, -43.172896],
    'Belo Horizonte': [-19.9166813, -43.9344931],
    'Brasília': [-15.826691, -47.921822],
    'Salvador': [-12.971399, -38.501305]
}

# Criar o mapa com Folium
mapa = folium.Map(location=[-14.235004, -51.92528], zoom_start=4)  # Coordenadas aproximadas do Brasil

# Adicionar marcadores para cada cidade
for cidade, coords in coordenadas_cidades.items():
    indice = indices[cidade]
    folium.Marker(
        location=coords,
        popup=f"{cidade}: {indice}",
        tooltip=f"{cidade} ({indice})",
        icon=folium.Icon(color="green" if indice > 70 else "red")
    ).add_to(mapa)

# Exibir mapa no Streamlit
st.subheader("Mapa Interativo")
st_folium(mapa, width=700, height=500)

# Converta os dados para DataFrame
df = pd.DataFrame(list(indices.items()), columns=['Cidade', 'Índice de Sustentabilidade'])

# Título do dashboard
st.title("Índice de Sustentabilidade Urbana - Principais Cidades Brasileiras")

# Gráfico interativo com Plotly
fig = px.bar(
    df,
    x='Cidade',
    y='Índice de Sustentabilidade',
    color='Índice de Sustentabilidade',
    color_continuous_scale='viridis',
    title="Índice de Sustentabilidade por Cidade"
)

st.plotly_chart(fig, use_container_width=True, key="main_chart")  # Adicione a key aqui

# Adicionar tabela com os dados
st.subheader("Tabela de Dados")
st.dataframe(df)

# Adicionar explicação sobre o índice
st.markdown("""
### Sobre o Índice de Sustentabilidade
O índice foi calculado com base em dados geoespaciais e indicadores ambientais das cidades brasileiras.
Ele reflete fatores como cobertura vegetal (NDVI) e densidade urbana (NDBI).
""")

# Dados adicionais (exemplo)
dados_adicionais = {
    'São Paulo': {'Temperatura Média (°C)': 22.5, 'IDH': 0.805, 'Área Verde (m²/hab)': 15},
    'Rio de Janeiro': {'Temperatura Média (°C)': 24.2, 'IDH': 0.799, 'Área Verde (m²/hab)': 12},
    'Belo Horizonte': {'Temperatura Média (°C)': 21.8, 'IDH': 0.810, 'Área Verde (m²/hab)': 18},
    'Brasília': {'Temperatura Média (°C)': 23.4, 'IDH': 0.824, 'Área Verde (m²/hab)': 25},
    'Salvador': {'Temperatura Média (°C)': 26.3, 'IDH': 0.759, 'Área Verde (m²/hab)': 10}
}

# Adicione os índices de sustentabilidade aos dados adicionais
for cidade in dados_adicionais:
    dados_adicionais[cidade]['Índice de Sustentabilidade'] = indices[cidade]

# Converta para DataFrame
df_adicional = pd.DataFrame(dados_adicionais).T.reset_index()
df_adicional.rename(columns={'index': 'Cidade'}, inplace=True)

# Exiba no Streamlit
st.subheader("Indicadores Adicionais")
st.dataframe(df_adicional)

# Filtro de cidades na barra lateral com key única
cidade_selecionada_sidebar = st.sidebar.selectbox(
    "Selecione uma cidade na barra lateral:", df['Cidade'], key="sidebar_city_select"
)

# Filtro de intervalo do índice na barra lateral com key única
indice_min_sidebar, indice_max_sidebar = st.sidebar.slider(
    "Filtrar Índice de Sustentabilidade na barra lateral:",
    min_value=int(df['Índice de Sustentabilidade'].min()),
    max_value=int(df['Índice de Sustentabilidade'].max()),
    value=(60, 90),
    key="sidebar_slider"
)

# Filtro de cidades na seção principal com key única
cidade_selecionada_main = st.selectbox(
    "Selecione uma cidade na seção principal:", df['Cidade'], key="main_city_select"
)

# Filtro de intervalo do índice na seção principal com key única
indice_min_main, indice_max_main = st.slider(
    "Filtrar Índice de Sustentabilidade na seção principal:",
    min_value=int(df['Índice de Sustentabilidade'].min()),
    max_value=int(df['Índice de Sustentabilidade'].max()),
    value=(60, 90),
    key="main_slider"
)

# Filtrar os dados com base nos filtros da seção principal
df_filtrado_main = df[(df['Índice de Sustentabilidade'] >= indice_min_main) & 
                      (df['Índice de Sustentabilidade'] <= indice_max_main)]

# Atualizar gráfico com base nos filtros da seção principal
fig_filtrado_main = px.bar(
    df_filtrado_main,
    x='Cidade',
    y='Índice de Sustentabilidade',
    color='Índice de Sustentabilidade',
    title="Índice Filtrado na Seção Principal"
)
st.plotly_chart(fig_filtrado_main, use_container_width=True, key="filtered_chart_main")

st.plotly_chart(plot_comparacao_idh_area_verde(df_adicional), key="idh_area_chart")  # Adicione a key aqui
st.plotly_chart(plot_radar(df_adicional), key="radar_chart")  # Adicione a key aqui

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(df)

st.download_button(
   label="Baixar Dados em CSV",
   data=csv,
   file_name='sustentabilidade_cidades.csv',
   mime='text/csv'
)
