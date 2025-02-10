import streamlit as st
import pandas as pd
import datetime
import os
from datetime import date, timedelta

# Nome do arquivo para salvar os jogos agendados
SCHEDULE_FILE = "agendamentos.csv"

# Função para carregar os jogos agendados do arquivo CSV
def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        return pd.read_csv(SCHEDULE_FILE, parse_dates=["Data"])
    return pd.DataFrame(columns=["Data", "Horario", "Classe", "Grupo", "Jogador1", "Jogador2"])

# Função para salvar os jogos agendados no arquivo CSV
def save_schedule(schedule):
    schedule.to_csv(SCHEDULE_FILE, index=False)

# Função para criar o calendário
def create_calendar(start_date, end_date, schedule):
    calendar = {}
    current_date = start_date
    while current_date <= end_date:
        calendar[current_date] = 0
        current_date += timedelta(days=1)
    
    for game_date in schedule["Data"]:
        if game_date.date() in calendar:
            calendar[game_date.date()] += 1
    
    return calendar

# Função para exibir o calendário de forma visual
def display_calendar(calendar, current_month):
    st.write("### Calendário de Jogos")
    
    # Dias da semana
    dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    
    # Cria uma tabela para o calendário
    colunas = st.columns(7)
    
    # Exibe os dias da semana como cabeçalho
    for i, dia in enumerate(dias_semana):
        colunas[i].write(f"**{dia}**")
    
    # Exibe os dias do mês
    current_date = date(current_month.year, current_month.month, 1)
    
    # Encontra o dia da semana do primeiro dia do mês (0 = Segunda, 6 = Domingo)
    first_day_weekday = current_date.weekday()  # weekday() retorna 0 para Segunda, 6 para Domingo
    
    # Preenche os dias vazios no início do mês
    for i in range(first_day_weekday):
        colunas[i].write("")  # Espaço vazio para alinhar o primeiro dia do mês
    
    # Exibe os dias do mês
    while current_date.month == current_month.month:
        # Define a cor do fundo com base no número de jogos
        count = calendar.get(current_date, 0)
        if count == 0:
            color = "#BBDEFB"  # Azul mais escuro
        elif 1 <= count <= 2:
            color = "#FFF59D"  # Amarelo mais escuro
        else:
            color = "#EF9A9A"  # Vermelho mais escuro
        
        # Exibe o dia no calendário
        col_index = current_date.weekday()  # 0 = Segunda, 6 = Domingo
        with colunas[col_index]:
            st.markdown(
                f"<div style='background-color:{color}; padding:10px; margin:2px; border-radius:5px; text-align:center; color:black;'>"
                f"<strong>{current_date.day}</strong><br>{count} jogo(s)"
                f"</div>",
                unsafe_allow_html=True
            )
        
        current_date += timedelta(days=1)
        
        # Se o dia da semana for Domingo (6), pula para a próxima linha
        if current_date.weekday() == 0:
            st.write("")  # Adiciona uma linha em branco para separar as semanas

# Função para avaliar a meta de jogos por semana
def evaluate_weekly_goal(schedule, start_date, end_date):
    weekly_goals = {}
    current_date = start_date
    while current_date <= end_date:
        week_start = datetime.datetime.combine(current_date, datetime.time(0, 0))  # Converte para datetime
        week_end = week_start + timedelta(days=6)
        games_in_week = len(schedule[(schedule["Data"] >= week_start) & (schedule["Data"] <= week_end)])
        weekly_goals[current_date] = games_in_week
        current_date = week_end.date() + timedelta(days=1)
    
    return weekly_goals

# Função para excluir um jogo
def delete_game(index):
    st.session_state.schedule = st.session_state.schedule.drop(index).reset_index(drop=True)
    save_schedule(st.session_state.schedule)
    st.success("Jogo excluído com sucesso!")
    st.experimental_rerun()  # Recarrega a página para atualizar a lista

# Inicialização do Streamlit
st.title("🎾 Agendamento de Jogos do Torneio de Tênis")

# Definição do período do torneio
start_date = date(2025, 2, 3)
end_date = date(2025, 3, 16)

# Lista de jogadores
jogadores = [
   "Airton Barata",
    "Augusto Silveira Espíndola",
    "Bruno Casale",
    "Carlos Frederico Da Costa",
    "Danilo Alves",
    "Denilson Montezani",
    "Emivaldo Feitosa",
    "Fagner Bantim",
    "Fernando Lino",
    "Fernando Sales Guedes",
    "Gustavo Avila",
    "Italo Araújo",
    "Jalmir Moreno Fernandes",
    "João Paulo Sampaio Rezende",
    "Joel Pereira Silva",
    "José Humberto Silva Junior",
    "Júnior Neres",
    "Luiz da Trindade Soares Júnior Júnior",
    "Lupesse Santana",
    "Mateus Moury",
    "Matheus Costa Silva",
    "Maximiliano Moura Costa",
    "Paulo Pedrosa",
    "Rhuan Teixeira",
    "Sandro Mesquita",
    "Sidney Santos",
    "Thiago Pinho",
    "Tulio Ourique",
    "Vinicius Paiva",
    "Willian F",
    "Wilson"
]

# Carregar os jogos agendados
if 'schedule' not in st.session_state:
    st.session_state.schedule = load_schedule()

# Seção para agendar novos jogos
st.write("### 🗓️ Agendar Novo Jogo")
with st.form("Agendar Jogo"):
    col1, col2 = st.columns(2)
    with col1:
        game_date = st.date_input("Data do Jogo", min_value=start_date, max_value=end_date)
    with col2:
        game_time = st.time_input("Horário do Jogo", value=datetime.time(10, 0))  # Horário padrão: 10:00
    
    class_type = st.selectbox("Classe", ["B", "C"])
    group = st.selectbox("Grupo", [1, 2, 3, 4])
    player1 = st.selectbox("Jogador 1", options=jogadores)
    player2 = st.selectbox("Jogador 2", options=jogadores)
    submit_button = st.form_submit_button("Agendar Jogo")

    if submit_button:
        if player1 == player2:
            st.error("Os jogadores devem ser diferentes.")
        else:
            # Combina data e horário em um único campo de data/hora
            game_datetime = datetime.datetime.combine(game_date, game_time)
            new_game = pd.DataFrame({
                "Data": [game_datetime],
                "Horario": [game_time.strftime("%H:%M")],  # Salva o horário separadamente
                "Classe": [class_type],
                "Grupo": [group],
                "Jogador1": [player1],
                "Jogador2": [player2]
            })
            st.session_state.schedule = pd.concat([st.session_state.schedule, new_game], ignore_index=True)
            save_schedule(st.session_state.schedule)
            st.success(f"✅ Jogo agendado para {game_datetime.strftime('%d/%m/%Y %H:%M')} entre {player1} e {player2} (Grupo {group}, Classe {class_type}).")

# Navegação entre meses
if 'current_month' not in st.session_state:
    st.session_state.current_month = start_date.replace(day=1)  # Começa no primeiro dia do mês inicial

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("◀️ Mês Anterior"):
        st.session_state.current_month = st.session_state.current_month - timedelta(days=1)
        st.session_state.current_month = st.session_state.current_month.replace(day=1)
with col3:
    if st.button("Mês Seguinte ▶️"):
        st.session_state.current_month = st.session_state.current_month + timedelta(days=31)
        st.session_state.current_month = st.session_state.current_month.replace(day=1)

# Exibe o calendário
calendar = create_calendar(start_date, end_date, st.session_state.schedule)
display_calendar(calendar, st.session_state.current_month)

# Exibição da lista de jogos agendados
st.write("### 📜 Lista de Jogos Agendados")

# Filtros opcionais
st.write("#### 🔍 Filtros (Opcional)")
with st.expander("Clique para expandir os filtros"):
    # Filtro por dia
    filter_by_date = st.checkbox("Filtrar por dia")
    selected_date = None
    if filter_by_date:
        selected_date = st.date_input("Selecione o dia", min_value=start_date, max_value=end_date)

    # Filtro por classe
    filter_by_class = st.checkbox("Filtrar por classe")
    selected_class = None
    if filter_by_class:
        selected_class = st.selectbox("Selecione a classe", ["B", "C"])

    # Filtro por grupo (só aparece se uma classe for selecionada)
    filter_by_group = False
    selected_group = None
    if filter_by_class and selected_class:
        filter_by_group = st.checkbox("Filtrar por grupo")
        if filter_by_group:
            selected_group = st.selectbox("Selecione o grupo", [1, 2, 3, 4])

# Aplicar filtros (se selecionados)
filtered_schedule = st.session_state.schedule.copy()

if filter_by_date and selected_date:
    filtered_schedule = filtered_schedule[filtered_schedule["Data"].dt.date == selected_date]

if filter_by_class and selected_class:
    filtered_schedule = filtered_schedule[filtered_schedule["Classe"] == selected_class]

if filter_by_group and selected_group:
    filtered_schedule = filtered_schedule[filtered_schedule["Grupo"] == selected_group]

# Ordenar a lista de jogos por data (da mais recente para a mais futura)
filtered_schedule = filtered_schedule.sort_values(by="Data", ascending=True)

# Exibição da lista de jogos
if not filtered_schedule.empty:
    for index, row in filtered_schedule.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 2, 2])
        with col1:
            st.write(f"**Data:** {row['Data'].strftime('%d/%m/%Y %H:%M')}")
        with col2:
            st.write(f"**Classe:** {row['Classe']}")
        with col3:
            st.write(f"**Grupo:** {row['Grupo']}")
        with col4:
            st.write(f"**Jogador 1:** {row['Jogador1']}")
        with col5:
            st.write(f"**Jogador 2:** {row['Jogador2']}")
        with col6:
            if st.button(f"Excluir Jogo {index + 1}", key=f"delete_{index}"):
                delete_game(index)
else:
    st.write("Nenhum jogo encontrado com os filtros selecionados.")

# Exibição do total de jogos agendados
st.write(f"### 📋 Total de Jogos Agendados: {len(st.session_state.schedule)}/48")

# Avaliação da meta de jogos por semana
st.write("### 📊 Avaliação de Jogos por Semana")
weekly_goals = evaluate_weekly_goal(st.session_state.schedule, start_date, end_date)
for week_start, games_in_week in weekly_goals.items():
    week_end = week_start + timedelta(days=6)
    st.write(f"**Semana de {week_start.strftime('%d/%m/%Y')} a {week_end.strftime('%d/%m/%Y')}:** {games_in_week} jogos agendados (Meta: 10 jogos)")
    if games_in_week < 10:
        st.error("Meta não atingida.")
    elif games_in_week > 10:
        st.warning("Meta excedida.")
    else:
        st.success("Meta atingida.")
