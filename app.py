import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Função para carregar os jogos do CSV
def carregar_jogos():
    try:
        jogos = pd.read_csv('jogos_pre_cadastrados.csv', parse_dates=['Data'])
        jogos = jogos.sort_values(by='Data', ascending=False)
        return jogos
    except FileNotFoundError:
        return pd.DataFrame(columns=['Data', 'Jogador1', 'Jogador2', 'Classe', 'Grupo'])

# Função para salvar os jogos no CSV
def salvar_jogos(jogos):
    jogos.to_csv('jogos_pre_cadastrados.csv', index=False)

# Função para exibir o calendário
def exibir_calendario(jogos):
    st.subheader("Calendário de Jogos")
    
    # Definir o período de 05/fev até 16/mar
    start_date = datetime(2023, 2, 5)
    end_date = datetime(2023, 3, 16)
    date_range = pd.date_range(start_date, end_date)
    
    # Contar o número de jogos por dia
    jogos_por_dia = jogos['Data'].value_counts().reindex(date_range, fill_value=0)
    
    # Criar o calendário visual
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, date in enumerate(date_range):
        num_jogos = jogos_por_dia[date]
        if num_jogos == 0:
            color = 'blue'
        elif 1 <= num_jogos <= 2:
            color = 'yellow'
        else:
            color = 'red'
        
        ax.add_patch(plt.Rectangle((i % 7, i // 7), 1, 1, color=color, alpha=0.5))
        ax.text(i % 7 + 0.5, i // 7 + 0.5, f"{date.day}\n{num_jogos} jogos", 
                ha='center', va='center', fontsize=8)
    
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 6)
    ax.set_xticks(range(7))
    ax.set_xticklabels(['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'])
    ax.set_yticks(range(6))
    ax.set_yticklabels(['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4', 'Semana 5', 'Semana 6'])
    ax.set_title("Fevereiro - Março 2023")
    ax.set_aspect('equal')
    ax.axis('off')
    
    st.pyplot(fig)

# Função principal
def main():
    st.title("Programação de Jogos de Tênis")
    
    # Carregar jogos
    jogos = carregar_jogos()
    
    # Filtros
    st.sidebar.header("Filtros")
    filtro_dia = st.sidebar.date_input("Filtrar por dia", value=None)
    filtro_jogador = st.sidebar.text_input("Filtrar por jogador")
    filtro_classe = st.sidebar.selectbox("Filtrar por classe", ['Todas', 'B', 'C'])
    filtro_grupo = st.sidebar.selectbox("Filtrar por grupo", ['Todos', '1', '2', '3', '4'])
    
    # Aplicar filtros
    if filtro_dia:
        jogos = jogos[jogos['Data'].dt.date == filtro_dia]
    if filtro_jogador:
        jogos = jogos[(jogos['Jogador1'] == filtro_jogador) | (jogos['Jogador2'] == filtro_jogador)]
    if filtro_classe != 'Todas':
        jogos = jogos[jogos['Classe'] == filtro_classe]
    if filtro_grupo != 'Todos':
        jogos = jogos[jogos['Grupo'] == int(filtro_grupo)]
    
    # Exibir calendário
    exibir_calendario(jogos)
    
    # Exibir jogos filtrados
    st.subheader("Jogos Filtrados")
    st.write(jogos)
    
    # Editar jogos
    st.sidebar.header("Editar Jogos")
    editar_data = st.sidebar.date_input("Editar data do jogo", value=None)
    editar_jogador1 = st.sidebar.text_input("Editar Jogador 1")
    editar_jogador2 = st.sidebar.text_input("Editar Jogador 2")
    editar_classe = st.sidebar.selectbox("Editar classe", ['B', 'C'])
    editar_grupo = st.sidebar.selectbox("Editar grupo", ['1', '2', '3', '4'])
    
    if st.sidebar.button("Salvar Edição"):
        novo_jogo = pd.DataFrame({
            'Data': [editar_data],
            'Jogador1': [editar_jogador1],
            'Jogador2': [editar_jogador2],
            'Classe': [editar_classe],
            'Grupo': [editar_grupo]
        })
        jogos = pd.concat([jogos, novo_jogo], ignore_index=True)
        salvar_jogos(jogos)
        st.success("Jogo salvo com sucesso!")
    
    if st.sidebar.button("Limpar Agendamentos"):
        jogos = pd.DataFrame(columns=['Data', 'Jogador1', 'Jogador2', 'Classe', 'Grupo'])
        salvar_jogos(jogos)
        st.success("Agendamentos limpos com sucesso!")

if __name__ == "__main__":
    main()
