import matplotlib.pyplot as plt
import seaborn as sns
import folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Tuple

def create_interactive_map(city_coordinates: Dict[str, Tuple[float, float]],  
                         sustainability_indices: Dict[str, float]) -> folium.Map:
    """Cria um mapa interativo com marcadores para cada cidade."""
    # Ponto central do Brasil como fallback
    m = folium.Map(location=[-14.235004, -51.92528], zoom_start=4)
    
    for city, coords in city_coordinates.items():
        if None in coords or city not in sustainability_indices:
            continue
            
        indice = sustainability_indices.get(city, None)
        
        # Verifica se o índice é válido antes de formatar
        if indice is None:
            popup_text = f"<b>{city}</b><br>Índice: Não disponível"
        else:
            popup_text = f"<b>{city}</b><br>Índice: {indice:.2f}"
        
        # Cor baseada no valor do índice
        if indice is None:
            color = "gray"
        else:
            color = "green" if indice > 70 else "orange" if indice > 50 else "red"
        
        folium.Marker(
            location=coords,
            popup=popup_text,
            tooltip=f"{city} ({indice:.2f}" if indice is not None else "N/D",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)
    
    return m


def plot_comparacao_idh_area_verde(df):
    try:
        # Verifica se o DataFrame tem dados necessários
        required_cols = ['Cidade', 'IDH', 'Área Verde (m²/hab)', 'Índice de Sustentabilidade']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("DataFrame não contém colunas necessárias")
        
        # Filtra apenas linhas com dados válidos
        plot_df = df.dropna(subset=['IDH', 'Área Verde (m²/hab)']).copy()
        
        # Garante que o tamanho seja positivo
        plot_df['Índice de Sustentabilidade'] = plot_df['Índice de Sustentabilidade'].fillna(0).clip(lower=0)
        
        # Cria gráfico apenas se houver dados
        if len(plot_df) > 0:
            fig = px.scatter(
                plot_df,
                x="IDH",
                y="Área Verde (m²/hab)",
                size="Índice de Sustentabilidade",
                color="Cidade",
                hover_name="Cidade",
                size_max=30,
                title="Relação entre IDH e Área Verde"
            )
            return fig
        else:
            return px.scatter(title="Sem dados válidos para plotar")
            
    except Exception as e:
        print(f"Erro no plot: {str(e)}")
        return px.scatter(title=f"Erro: {str(e)}")

def plot_radar(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico radar com múltiplos indicadores."""
    required_cols = ['Cidade', 'Temperatura Média (°C)', 'IDH', 'Área Verde (m²/hab)']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("DataFrame não contém todas as colunas necessárias")
    
    fig = go.Figure()
    
    for _, row in df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[
                row['Temperatura Média (°C)'],
                row['IDH'] * 100,  # Converter para porcentagem
                row['Área Verde (m²/hab)']
            ],
            theta=['Temperatura Média', 'IDH (%)', 'Área Verde'],
            fill='toself',
            name=row['Cidade']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]  # Padroniza escala para melhor comparação
            )),
        showlegend=True,
        title="Comparação de Indicadores por Cidade",
        legend_title="Cidades",
        title_font=dict(size=16)
    )
    
    return fig

def plot_sustainability_index(indices: Dict[str, float]) -> None:
    """Cria gráfico de barras do índice de sustentabilidade."""
    if not indices:
        raise ValueError("Dicionário de índices vazio")
    
    df = pd.DataFrame.from_dict(indices, orient='index', columns=['Índice'])
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Cidade'}, inplace=True)
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        x='Cidade',
        y='Índice',
        data=df,
        palette='viridis'
    )
    
    # Adiciona valores nas barras
    for p in ax.patches:
        ax.annotate(
            f'{p.get_height():.1f}',
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center',
            xytext=(0, 10), textcoords='offset points'
        )
    
    plt.title('Índice de Sustentabilidade por Cidade', fontsize=14)
    plt.ylabel('Índice', fontsize=12)
    plt.xlabel('')
    plt.xticks(rotation=45)
    plt.ylim(0, 100)  # Assume que o índice vai de 0 a 100
    plt.tight_layout()
    
    plt.show()
