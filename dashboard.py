import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from visualization import plot_comparacao_idh_area_verde, plot_radar, plot_sustainability_index
import json  # Import necessário para manipular JSON

# Função para carregar os dados reais gerados pelo main.py
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("resultados_sustentabilidade.csv")  # Arquivo gerado pelo main.py
        return df
    except FileNotFoundError:
        st.error("Arquivo resultados_sustentabilidade.csv não encontrado. Execute o main.py primeiro.")
        return pd.DataFrame()  # Retorna um DataFrame vazio se o arquivo não for encontrado

# Carregar os dados reais
df = load_data()

if not df.empty:
    # Título do dashboard
    st.title("Índice de Sustentabilidade Urbana - Dados Reais")

    # Layout com colunas para gráficos e mapa lado a lado
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico interativo com Plotly
        fig = px.bar(
            df,
            x='Cidade',
            y='Índice de Sustentabilidade',
            color='Índice de Sustentabilidade',
            color_continuous_scale='viridis',
            title="Índice de Sustentabilidade por Cidade"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Criar o mapa interativo com Folium
        mapa = folium.Map(location=[-14.235004, -51.92528], zoom_start=4)
        for _, row in df.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Cidade']}: {row['Índice de Sustentabilidade']}",
                tooltip=f"{row['Cidade']} ({row['Índice de Sustentabilidade']})",
                icon=folium.Icon(color="green" if row['Índice de Sustentabilidade'] > 70 else "red")
            ).add_to(mapa)
        
        st.subheader("Mapa Interativo")
        st_folium(mapa, width=700, height=500)

    # Exibir tabela com os dados carregados
    st.subheader("Tabela de Dados Reais")
    st.dataframe(df)

    # Filtros na barra lateral
    st.sidebar.title("Filtros")
    cidade_selecionada_sidebar = st.sidebar.selectbox(
        "Selecione uma cidade na barra lateral:", df['Cidade']
    )

    # Corrigir slider para retornar intervalo (mínimo e máximo)
    indice_min_sidebar, indice_max_sidebar = st.sidebar.slider(
        "Filtrar Índice de Sustentabilidade:",
        min_value=int(df['Índice de Sustentabilidade'].min()),
        max_value=int(df['Índice de Sustentabilidade'].max()),
        value=(60, 90)  # Certifique-se de usar uma tupla aqui!
    )

    # Filtrar os dados com base nos filtros da barra lateral
    df_filtrado_sidebar = df[(df['Índice de Sustentabilidade'] >= indice_min_sidebar) & 
                             (df['Índice de Sustentabilidade'] <= indice_max_sidebar)]

    # Atualizar gráfico com base nos filtros da barra lateral
    fig_filtrado_sidebar = px.bar(
        df_filtrado_sidebar,
        x='Cidade',
        y='Índice de Sustentabilidade',
        color='Índice de Sustentabilidade',
        title="Índice Filtrado na Barra Lateral"
    )
    st.sidebar.plotly_chart(fig_filtrado_sidebar)

    # Gráficos comparativos (exemplo: dispersão e radar)
    if all(col in df.columns for col in ['IDH', 'Área Verde (m²/hab)', 'Temperatura Média (°C)']):
        st.plotly_chart(plot_comparacao_idh_area_verde(df), key="idh_area_chart")
        st.plotly_chart(plot_radar(df), key="radar_chart")
    else:
        st.warning("Dados adicionais necessários para gráficos comparativos não estão disponíveis.")

    # Gráfico estático (Matplotlib/Seaborn)
    st.subheader("Gráfico Estático - Índice de Sustentabilidade")
    plot_sustainability_index(dict(zip(df['Cidade'], df['Índice de Sustentabilidade'])))

    # Função para exportação dos dados em CSV diretamente no dashboard
    @st.cache_data
    def convert_df_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(df)

    st.download_button(
       label="Baixar Dados em CSV",
       data=csv,
       file_name='dados_sustentabilidade.csv',
       mime='text/csv'
    )

    # Função para exportação dos dados em JSON diretamente no dashboard
    @st.cache_data
    def convert_df_to_json(dataframe):
        return dataframe.to_json(orient='records', indent=4).encode('utf-8')

    json_data = convert_df_to_json(df)

    st.download_button(
       label="Baixar Dados em JSON",
       data=json_data,
       file_name='dados_sustentabilidade.json',
       mime='application/json'
    )
else:
    st.warning("Nenhum dado disponível. Execute o main.py para gerar os dados reais.")
