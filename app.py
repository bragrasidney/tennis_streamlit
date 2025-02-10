import streamlit as st
import pandas as pd
import datetime
import os
from datetime import date, timedelta

# Nome do arquivo para salvar os jogos agendados
SCHEDULE_FILE = "agendamentos.csv"
RESULTS_FILE = "resultados.csv"

# Função para carregar os jogos agendados do arquivo CSV
def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        return pd.read_csv(SCHEDULE_FILE, parse_dates=["Data"])
    return pd.DataFrame(columns=["Data", "Horario", "Classe", "Grupo", "Jogador1", "Jogador2"])

# Função para salvar os jogos agendados no arquivo CSV
def save_schedule(schedule):
    schedule.to_csv(SCHEDULE_FILE, index=False)

# Função para limpar o arquivo agendamentos.csv
def limpar_agendamentos():
    if os.path.exists("agendamentos.csv"):
        os.remove("agendamentos.csv")
        st.session_state.schedule = pd.DataFrame(columns=["Data", "Horario", "Classe", "Grupo", "Jogador1", "Jogador2"])
        st.success("Arquivo agendamentos.csv limpo com sucesso!")
    else:
        st.warning("O arquivo agendamentos.csv não existe.")

# Adicione um botão para limpar o arquivo
if st.button("Limpar arquivo agendamentos.csv"):
    limpar_agendamentos()
# Função para carregar os resultados dos jogos
def load_results():
    if os.path.exists(RESULTS_FILE):
        return pd.read_csv(RESULTS_FILE, parse_dates=["Data"])
    return pd.DataFrame(columns=["Data", "Horario", "Classe", "Grupo", "Jogador1", "Jogador2", "Vencedor", "Sets_Jogador1", "Sets_Jogador2", "Games_Jogador1", "Games_Jogador2", "Tiebreaks_Jogador1", "Tiebreaks_Jogador2"])

# Função para salvar os resultados dos jogos no arquivo CSV
def save_results(results):
    results.to_csv(RESULTS_FILE, index=False)

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

# Função para calcular estatísticas por grupo
def calculate_group_stats(results, group):
    stats = {}
    for _, row in results[results["Grupo"] == group].iterrows():
        jogador1 = row["Jogador1"]
        jogador2 = row["Jogador2"]
        vencedor = row["Vencedor"]
        sets_jogador1 = row["Sets_Jogador1"]
        sets_jogador2 = row["Sets_Jogador2"]
        games_jogador1 = row["Games_Jogador1"]
        games_jogador2 = row["Games_Jogador2"]
        tiebreaks_jogador1 = row["Tiebreaks_Jogador1"]
        tiebreaks_jogador2 = row["Tiebreaks_Jogador2"]

        # Inicializa as estatísticas dos jogadores, se necessário
        if jogador1 not in stats:
            stats[jogador1] = {"Jogos": 0, "Vitórias": 0, "Derrotas": 0, "Sets_Ganhos": 0, "Sets_Perdidos": 0, "Games_Ganhos": 0, "Games_Perdidos": 0, "Tiebreaks_Ganhos": 0, "Tiebreaks_Perdidos": 0}
        if jogador2 not in stats:
            stats[jogador2] = {"Jogos": 0, "Vitórias": 0, "Derrotas": 0, "Sets_Ganhos": 0, "Sets_Perdidos": 0, "Games_Ganhos": 0, "Games_Perdidos": 0, "Tiebreaks_Ganhos": 0, "Tiebreaks_Perdidos": 0}

        # Atualiza as estatísticas dos jogadores
        stats[jogador1]["Jogos"] += 1
        stats[jogador2]["Jogos"] += 1

        if vencedor == jogador1:
            stats[jogador1]["Vitórias"] += 1
            stats[jogador2]["Derrotas"] += 1
        else:
            stats[jogador2]["Vitórias"] += 1
            stats[jogador1]["Derrotas"] += 1

        stats[jogador1]["Sets_Ganhos"] += sets_jogador1
        stats[jogador1]["Sets_Perdidos"] += sets_jogador2
        stats[jogador2]["Sets_Ganhos"] += sets_jogador2
        stats[jogador2]["Sets_Perdidos"] += sets_jogador1

        stats[jogador1]["Games_Ganhos"] += games_jogador1
        stats[jogador1]["Games_Perdidos"] += games_jogador2
        stats[jogador2]["Games_Ganhos"] += games_jogador2
        stats[jogador2]["Games_Perdidos"] += games_jogador1

        stats[jogador1]["Tiebreaks_Ganhos"] += tiebreaks_jogador1
        stats[jogador1]["Tiebreaks_Perdidos"] += tiebreaks_jogador2
        stats[jogador2]["Tiebreaks_Ganhos"] += tiebreaks_jogador2
        stats[jogador2]["Tiebreaks_Perdidos"] += tiebreaks_jogador1

    # Converte as estatísticas em um DataFrame
    stats_df = pd.DataFrame.from_dict(stats, orient="index")
    stats_df["Saldo_Sets"] = stats_df["Sets_Ganhos"] - stats_df["Sets_Perdidos"]
    stats_df["Saldo_Games"] = stats_df["Games_Ganhos"] - stats_df["Games_Perdidos"]
    stats_df["Saldo_Tiebreaks"] = stats_df["Tiebreaks_Ganhos"] - stats_df["Tiebreaks_Perdidos"]

    # Ordena os jogadores por vitórias, saldo de sets, saldo de games e saldo de tiebreaks
    stats_df = stats_df.sort_values(by=["Vitórias", "Saldo_Sets", "Saldo_Games", "Saldo_Tiebreaks"], ascending=False)
    return stats_df

# Inicialização do Streamlit
st.title("🎾 Agendamento de Jogos do Torneio de Tênis")

# Definição do período do torneio
start_date = date(2025, 2, 3)
end_date = date(2025, 3, 16)

# Lista de jogadores
jogadores = [
    "Airton Barata", "Augusto E", "Carlos Frederico", "Danilo Alves", "Fernando Lino",
    "Joel Pereira", "José Humberto", "Luiz Jr", "Lupesse Santana", "Matheus C",
    "Túlio Ourique", "Vinicius Paiva", "Walmir Irineu", "Walter C", "Warwick Melo", "Willian F"
]

# Carregar os jogos agendados
if 'schedule' not in st.session_state:
    st.session_state.schedule = load_schedule()
    # Função para verificar se um jogo já existe no schedule
def jogo_ja_existe(jogo, schedule):
    return ((schedule["Data"] == jogo["Data"]) &
            (schedule["Horario"] == jogo["Horario"]) &
            (schedule["Classe"] == jogo["Classe"]) &
            (schedule["Grupo"] == jogo["Grupo"]) &
            (schedule["Jogador1"] == jogo["Jogador1"]) &
            (schedule["Jogador2"] == jogo["Jogador2"])).any()

# Carregar os jogos pré-cadastrados
if os.path.exists("jogos_pre_cadastrados.csv"):
    pre_cadastrados = pd.read_csv("jogos_pre_cadastrados.csv", parse_dates=["Data"])
    
    # Verificar se os jogos pré-cadastrados já foram adicionados
    if 'schedule' not in st.session_state:
        st.session_state.schedule = load_schedule()
    
    # Adicionar apenas os jogos que ainda não estão no schedule
    novos_jogos = []
    for _, jogo in pre_cadastrados.iterrows():
        if not jogo_ja_existe(jogo, st.session_state.schedule):
            # Converter a string de horário para um objeto datetime.time
            horario = datetime.datetime.strptime(jogo["Horario"], "%H:%M").time()
            # Combinar data e horário
            data_horario = datetime.datetime.combine(jogo["Data"].date(), horario)
            # Criar um novo jogo com a data e horário combinados
            novo_jogo = {
                "Data": data_horario,
                "Horario": jogo["Horario"],
                "Classe": jogo["Classe"],
                "Grupo": jogo["Grupo"],
                "Jogador1": jogo["Jogador1"],
                "Jogador2": jogo["Jogador2"]
            }
            novos_jogos.append(novo_jogo)
    
    if novos_jogos:
        novos_jogos_df = pd.DataFrame(novos_jogos)
        st.session_state.schedule = pd.concat([st.session_state.schedule, novos_jogos_df], ignore_index=True)
        save_schedule(st.session_state.schedule)
        st.success(f"{len(novos_jogos)} jogos pré-cadastrados adicionados com sucesso!")
# Carregar os resultados dos jogos
if 'results' not in st.session_state:
    st.session_state.results = load_results()

# Inicializar o mês atual no session_state
if 'current_month' not in st.session_state:
    st.session_state.current_month = start_date.replace(day=1)  # Começa no primeiro dia do mês inicial

# Abas para agendamento e resultados
tab1, tab2 = st.tabs(["Agendamento de Jogos", "Resultados e Estatísticas"])

with tab1:
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

with tab2:
    st.write("### 🎾 Resultados dos Jogos")

    # Seção para inserir resultados
    st.write("#### 📝 Inserir Resultado")
    with st.form("Inserir Resultado"):
        # Selecionar o jogo
        jogos_agendados = st.session_state.schedule.copy()
        
        # Verifica se o DataFrame não está vazio e se as colunas existem
        if not jogos_agendados.empty and 'Jogador1' in jogos_agendados.columns and 'Jogador2' in jogos_agendados.columns:
            # Cria a coluna "Jogo" com a descrição do jogo
            jogos_agendados["Jogo"] = jogos_agendados.apply(lambda row: f"{row['Jogador1']} vs {row['Jogador2']}", axis=1)
            
            # Seleciona o jogo para inserir o resultado
            jogo_selecionado = st.selectbox("Selecione o jogo", jogos_agendados["Jogo"])
            
            # Obtém os detalhes do jogo selecionado
            jogo_info = jogos_agendados[jogos_agendados["Jogo"] == jogo_selecionado].iloc[0]
            jogador1 = jogo_info["Jogador1"]
            jogador2 = jogo_info["Jogador2"]
            
            # Campos para inserir o resultado
            st.write(f"**Jogo selecionado:** {jogador1} vs {jogador2}")
            sets_jogador1 = st.number_input(f"Sets ganhos por {jogador1}", min_value=0, max_value=3, value=0)
            sets_jogador2 = st.number_input(f"Sets ganhos por {jogador2}", min_value=0, max_value=3, value=0)
            games_jogador1 = st.number_input(f"Games ganhos por {jogador1}", min_value=0, value=0)
            games_jogador2 = st.number_input(f"Games ganhos por {jogador2}", min_value=0, value=0)
            tiebreaks_jogador1 = st.number_input(f"Tiebreaks ganhos por {jogador1}", min_value=0, value=0)
            tiebreaks_jogador2 = st.number_input(f"Tiebreaks ganhos por {jogador2}", min_value=0, value=0)
            
            # Botão para salvar o resultado
            submit_resultado = st.form_submit_button("Salvar Resultado")
            
            if submit_resultado:
                # Determina o vencedor
                if sets_jogador1 > sets_jogador2:
                    vencedor = jogador1
                elif sets_jogador2 > sets_jogador1:
                    vencedor = jogador2
                else:
                    vencedor = "Empate"
                
                # Adiciona o resultado ao DataFrame de resultados
                novo_resultado = pd.DataFrame({
                    "Data": [jogo_info["Data"]],
                    "Horario": [jogo_info["Horario"]],
                    "Classe": [jogo_info["Classe"]],
                    "Grupo": [jogo_info["Grupo"]],
                    "Jogador1": [jogador1],
                    "Jogador2": [jogador2],
                    "Vencedor": [vencedor],
                    "Sets_Jogador1": [sets_jogador1],
                    "Sets_Jogador2": [sets_jogador2],
                    "Games_Jogador1": [games_jogador1],
                    "Games_Jogador2": [games_jogador2],
                    "Tiebreaks_Jogador1": [tiebreaks_jogador1],
                    "Tiebreaks_Jogador2": [tiebreaks_jogador2]
                })
                
                st.session_state.results = pd.concat([st.session_state.results, novo_resultado], ignore_index=True)
                save_results(st.session_state.results)
                st.success("Resultado salvo com sucesso!")
        else:
            st.warning("Nenhum jogo agendado encontrado.")

    # Exibição dos resultados
    st.write("### 📊 Resultados Registrados")
    if not st.session_state.results.empty:
        st.dataframe(st.session_state.results)
    else:
        st.write("Nenhum resultado registrado ainda.")

    # Filtros para exibir estatísticas por grupo
    st.write("#### 🔍 Filtros para Estatísticas")
    selected_class = st.selectbox("Selecione a classe", ["B", "C"])
    selected_group = st.selectbox("Selecione o grupo", [1, 2, 3, 4])

    # Calcula e exibe as estatísticas do grupo selecionado
    if not st.session_state.results.empty:
        stats_df = calculate_group_stats(st.session_state.results, selected_group)
        st.write(f"### 📈 Estatísticas do Grupo {selected_group} (Classe {selected_class})")
        st.dataframe(stats_df)
    else:
        st.write("Nenhum resultado registrado para calcular estatísticas.")
