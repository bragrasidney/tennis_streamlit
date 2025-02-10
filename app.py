import streamlit as st
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import json
import os

# Configuração das semanas do torneio
WEEKS = [
    {"number": 1, "start": date(2025, 2, 3), "end": date(2025, 2, 9), "target": 10},
    {"number": 2, "start": date(2025, 2, 10), "end": date(2025, 2, 16), "target": 10},
    {"number": 3, "start": date(2025, 2, 17), "end": date(2025, 2, 23), "target": 10},
    {"number": 4, "start": date(2025, 2, 24), "end": date(2025, 3, 2), "target": 10},
    {"number": 5, "start": date(2025, 3, 3), "end": date(2025, 3, 16), "target": 10},
]

# Função para carregar os agendamentos do arquivo JSON
def load_matches():
    if os.path.exists("matches.json"):
        with open("matches.json", "r") as file:
            return json.load(file)
    return []

# Função para salvar os agendamentos no arquivo JSON
def save_matches(matches):
    with open("matches.json", "w") as file:
        json.dump(matches, file)

def calculate_progress(matches):
    # Cria uma cópia das semanas para não modificar a original
    weeks = [week.copy() for week in WEEKS]

    # Inicializa dados das semanas (na cópia)
    for week in weeks:
        week["actual"] = 0
        week["cum_target"] = week["target"] * week["number"]
        week["status"] = "⚠️ Não iniciado"

    # Contabiliza jogos por semana
    for game in matches:
        game_date = datetime.strptime(game["data"], "%Y-%m-%d").date()
        for week in weeks:
            if week["start"] <= game_date <= week["end"]:
                week["actual"] += 1

    # Calcula métricas
    total_target = 48
    total_actual = sum(week["actual"] for week in weeks)
    remaining = max(total_target - total_actual, 0)
    percent = (total_actual / total_target) * 100

    # Calcula status por semana
    for week in weeks:
        week["cum_actual"] = sum(w["actual"] for w in weeks if w["number"] <= week["number"])
        week["saldo"] = week["actual"] - week["target"]
        week["status"] = "✅ Superavit" if week["saldo"] > 0 else "❌ Deficit" if week["saldo"] < 0 else "⏳ Meta atingida"

    return {
        "total_target": total_target,
        "total_actual": total_actual,
        "remaining": remaining,
        "percent": percent,
        "weeks_df": pd.DataFrame(weeks)  # Use a cópia atualizada
    }

def main():
    st.set_page_config(page_title="Agenda Torneio de Tênis", layout="wide")
    
    # Carrega os agendamentos salvos
    if 'matches' not in st.session_state:
        st.session_state.matches = load_matches()
    
    st.title("Agendamento de Jogos - 1º Open RNK PBS")
    
    # Formulário de cadastro
    with st.form("agendar_jogo"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            jogador1 = st.text_input("Jogador 1")
            classe = st.selectbox("Classe", ["B", "C", "D"])
            
        with col2:
            jogador2 = st.text_input("Jogador 2")
            if classe in ["B", "C"]:
                grupo = st.selectbox("Grupo", [1, 2, 3, 4])
            else:
                grupo = st.selectbox("Grupo", [1, 2])
                
        with col3:
            data = st.date_input("Data do jogo", min_value=WEEKS[0]["start"], max_value=WEEKS[-1]["end"])
            hora = st.time_input("Horário do jogo")
        
        if st.form_submit_button("Agendar Jogo"):
            if jogador1 and jogador2:
                novo_jogo = {
                    "data": data.strftime("%Y-%m-%d"),
                    "hora": hora.strftime("%H:%M"),
                    "classe": classe,
                    "grupo": grupo,
                    "jogador1": jogador1,
                    "jogador2": jogador2
                }
                st.session_state.matches.append(novo_jogo)
                save_matches(st.session_state.matches)  # Salva os agendamentos no arquivo
                st.success("Jogo agendado com sucesso!")
            else:
                st.error("Preencha todos os campos obrigatórios")

    # Lista de jogos agendados
    st.subheader("Jogos Agendados")
    
    if st.session_state.matches:
        # Converter para DataFrame e ordenar por data (mais recente primeiro)
        df = pd.DataFrame(st.session_state.matches)
        df['data_datetime'] = pd.to_datetime(df['data'])
        df = df.sort_values(by='data_datetime', ascending=True)

        # Formata a data para o padrão brasileiro (DD/MM/AAAA)
        df['data'] = df['data_datetime'].dt.strftime('%d/%m/%Y')
        df = df.drop('data_datetime', axis=1)
        
        # Filtros na barra lateral
        st.sidebar.header("Filtrar Jogos")
        filtro_jogador = st.sidebar.text_input("Filtrar por Jogador (nome parcial ou completo)")
        filtro_data = st.sidebar.date_input("Filtrar por Data", value=None)
        filtro_classe = st.sidebar.selectbox("Filtrar por Classe", ["Todas", "B", "C", "D"])

        # Filtro por grupo (só aparece se uma classe específica for selecionada)
        if filtro_classe != "Todas":
            if filtro_classe in ["B", "C"]:
                filtro_grupo = st.sidebar.selectbox("Filtrar por Grupo", ["Todos", 1, 2, 3, 4])
            else:
                filtro_grupo = st.sidebar.selectbox("Filtrar por Grupo", ["Todos", 1, 2])
        else:
            filtro_grupo = "Todos"

        # Aplicar filtros
        if filtro_jogador:
            df = df[df.apply(lambda row: filtro_jogador.lower() in row['jogador1'].lower() or 
                             filtro_jogador.lower() in row['jogador2'].lower(), axis=1)]
        
        if filtro_data:
            df = df[df['data'] == filtro_data.strftime('%d/%m/%Y')]
        
        if filtro_classe != "Todas":
            df = df[df['classe'] == filtro_classe]
        
        if filtro_grupo != "Todos":
            df = df[df['grupo'] == filtro_grupo]

        # Adiciona uma coluna com botões de exclusão
        df['Excluir'] = False
        edited_df = st.data_editor(
            df,
            column_config={
                "data": "Data",
                "hora": "Horário",
                "classe": "Classe",
                "grupo": "Grupo",
                "jogador1": "Jogador 1",
                "jogador2": "Jogador 2",
                "Excluir": st.column_config.CheckboxColumn("Excluir", help="Marque para excluir o jogo")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Verifica se algum jogo foi marcado para exclusão
        if edited_df['Excluir'].any():
            # Filtra os jogos que não foram marcados para exclusão
            jogos_para_excluir = edited_df[edited_df['Excluir']]
            st.session_state.matches = [
                match for match in st.session_state.matches
                if not (
                    match["data"] in jogos_para_excluir['data'].values and
                    match["hora"] in jogos_para_excluir['hora'].values and
                    match["classe"] in jogos_para_excluir['classe'].values and
                    match["grupo"] in jogos_para_excluir['grupo'].values and
                    match["jogador1"] in jogos_para_excluir['jogador1'].values and
                    match["jogador2"] in jogos_para_excluir['jogador2'].values
                )
            ]
            save_matches(st.session_state.matches)  # Salva a lista atualizada no arquivo
            st.success("Jogos selecionados excluídos com sucesso!")
            st.rerun()
        
        # Botão para limpar agenda
        if st.button("Limpar Todos os Jogos"):
            st.session_state.matches = []
            save_matches(st.session_state.matches)  # Salva a lista vazia no arquivo
            st.success("Todos os jogos foram removidos.")
            st.rerun()
    else:
        st.info("Nenhum jogo agendado ainda")

    # Seção de progresso
    st.header("Acompanhamento de Metas")
    
    if st.session_state.matches:
        progress = calculate_progress(st.session_state.matches)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Agendado", f"{progress['total_actual']}/48")
        col2.metric("Progresso Geral", f"{progress['percent']:.1f}%")
        col3.metric("Jogos Restantes", progress['remaining'])

        # Encontrando a semana atual
        today = date.today()
        current_week = None
        for week in WEEKS:
            if week["start"] <= today <= week["end"]:
                current_week = week
                break

        if current_week:
            col4.metric("Semana Atual", f"Semana {current_week['number']}")
        else:
            col4.metric("Semana Atual", "Torneio não iniciado ou finalizado")
        
        # Gráfico de barras comparativo
        fig = px.bar(progress['weeks_df'], 
                     x='number', 
                     y=['target', 'actual'], 
                     barmode='group',
                     labels={'number': 'Semana', 'value': 'Jogos'},
                     title="Meta vs Agendado por Semana")
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de progresso acumulado
        fig2 = px.line(progress['weeks_df'], 
                      x='number', 
                      y=['cum_target', 'cum_actual'],
                      labels={'number': 'Semana', 'value': 'Jogos'},
                      title="Progresso Acumulado")
        st.plotly_chart(fig2, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("Detalhamento por Semana")
        # Formata as colunas de data para o padrão brasileiro
        progress['weeks_df']['start'] = pd.to_datetime(progress['weeks_df']['start']).dt.strftime('%d/%m/%Y')
        progress['weeks_df']['end'] = pd.to_datetime(progress['weeks_df']['end']).dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            progress['weeks_df'][['number', 'start', 'end', 'target', 'actual', 'saldo', 'status']],
            column_config={
                "number": "Semana",
                "start": "Início",
                "end": "Fim",
                "target": "Meta",
                "actual": "Realizado",
                "saldo": "Saldo",
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nenhum jogo agendado ainda para cálculo de metas")

if __name__ == "__main__":
    main()
