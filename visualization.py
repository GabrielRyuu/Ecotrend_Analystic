import matplotlib.pyplot as plt
import seaborn as sns
import folium
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st  # Adicione esta importação para integrar ao Streamlit

def create_interactive_map(city_coordinates, sustainability_indices):
    m = folium.Map(location=[-14.235004, -51.92528], zoom_start=4)
    
    for city, coords in city_coordinates.items():
        indice = sustainability_indices[city]
        folium.Marker(
            location=coords,
            popup=f"<b>{city}</b><br>Índice de Sustentabilidade: {indice:.2f}",
            tooltip=f"{city} ({indice:.2f})",
            icon=folium.Icon(color="green" if indice > 70 else "red")
        ).add_to(m)
    
    return m

def plot_comparacao_idh_area_verde(df):
    fig_disp = px.scatter(
        df,
        x='IDH',
        y='Área Verde (m²/hab)',
        size='Índice de Sustentabilidade',
        color='Cidade',
        title="Comparação entre IDH e Área Verde por Cidade",
        labels={
            'IDH': "Índice de Desenvolvimento Humano (IDH)", 
            'Área Verde (m²/hab)': "Área Verde por Habitante (m²)"
        },
        size_max=40  
    )
    
    fig_disp.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    
    return fig_disp

def plot_radar(df):
    fig_radar = go.Figure()

    for i in range(len(df)):
        fig_radar.add_trace(go.Scatterpolar(
            r=[
                df.loc[i, "Temperatura Média (°C)"],
                df.loc[i, "IDH"] * 100,
                df.loc[i, "Área Verde (m²/hab)"]
            ],
            theta=["Temperatura Média", "IDH (%)", "Área Verde"],
            fill='toself',
            name=df.loc[i, "Cidade"]
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title="Indicadores Comparativos por Cidade",
        legend_title="Cidades"
    )
    
    return fig_radar

def plot_sustainability_index(indices):
    """
    Exibe um gráfico de barras dos índices de sustentabilidade no Streamlit.
    
    Parâmetros:
        indices (dict): Dicionário com os índices de sustentabilidade por cidade.
    """
    plt.figure(figsize=(12, 6))
    cores = sns.color_palette('viridis', len(indices))  
    ax = sns.barplot(
        x=list(indices.keys()), 
        y=list(indices.values()), 
        palette=cores
    )
    
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.0f}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 10), textcoords='offset points',
                    fontsize=10, color='black')

    plt.title('Índice de Sustentabilidade Urbana - Principais Cidades Brasileiras', fontsize=14)
    plt.ylabel('Índice de Sustentabilidade', fontsize=12)
    plt.xlabel('Cidades', fontsize=12)
    plt.xticks(rotation=45, fontsize=10)
    plt.tight_layout()
    
    # Exibe o gráfico no Streamlit
    st.pyplot(plt)
