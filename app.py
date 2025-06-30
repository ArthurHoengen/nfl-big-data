import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os

@st.cache_data
def load_parquet(file):
    return pd.read_parquet(file)

@st.cache_data
def load_tracking_for_play(game_id, play_id):
    dfs = []
    for i in range(1, 10):
        path = f"data/tracking_week_{i}.parquet"
        if os.path.exists(path):
            df = pd.read_parquet(
                path,
                columns=["gameId", "playId", "x", "y", "frameId", "displayName", "club", "nflId"]
            )
            df = df[(df["gameId"] == game_id) & (df["playId"] == play_id)]
            if not df.empty:
                dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

@st.cache_data
def load_players():
    return pd.read_parquet("data/players.parquet")

def calcular_velocidade(df):
    df = df.sort_values(['displayName', 'frameId']).copy()
    df[['x_prev', 'y_prev']] = df.groupby('displayName')[['x', 'y']].shift(1)
    df['dist'] = np.sqrt((df['x'] - df['x_prev'])**2 + (df['y'] - df['y_prev'])**2)
    tempo_entre_frames = 0.1  # Assumindo 10 fps
    df['velocidade'] = df['dist'] / tempo_entre_frames
    return df

# Início do app
st.set_page_config(layout="wide")
st.title("🏈 NFL Big Data Bowl Dashboard")

# Carrega dados
games = load_parquet("data/games.parquet")
plays = load_parquet("data/plays.parquet")
players = load_players()

teams = plays['possessionTeam'].dropna().unique()
team = st.selectbox("Selecione um time", sorted(teams))
team_plays = plays[plays['possessionTeam'] == team]
game_id = st.selectbox("Selecione um jogo", sorted(team_plays['gameId'].unique()))
play_id = st.selectbox("Selecione uma jogada", sorted(team_plays[team_plays['gameId'] == game_id]['playId'].unique()))
play_row = team_plays[(team_plays['gameId'] == game_id) & (team_plays['playId'] == play_id)]

if not play_row.empty:
    st.markdown(f"**Descrição da jogada:** {play_row.iloc[0]['playDescription']}")

with st.spinner("Carregando tracking da jogada..."):
    play_tracking = load_tracking_for_play(game_id, play_id)

if play_tracking.empty:
    st.warning("Dados de tracking não encontrados para essa jogada.")
    st.stop()

# Calcula velocidade
play_tracking = calcular_velocidade(play_tracking)

# ————————————
# Campo e animação com jogadores + bola + velocidade (velocidade no hover)
FIELD_LENGTH = 120
FIELD_WIDTH = 53.3
frames = sorted(play_tracking["frameId"].unique())
first_frame = play_tracking[play_tracking["frameId"] == frames[0]]

# Para a bola (club=='football'), vamos criar a linha da trajetória
bola_traj = play_tracking[play_tracking['club'] == 'football'].sort_values('frameId')

layout = go.Layout(
    title="🏈 Reexecução da Jogada com Velocidade",
    xaxis=dict(range=[0, FIELD_LENGTH], title="Jardas (Comprimento)", zeroline=False),
    yaxis=dict(range=[0, FIELD_WIDTH], title="Largura do Campo", zeroline=False),
    height=600,
    width=1000,
    showlegend=True,
    transition=dict(duration=0),
    sliders=[{
        "steps": [{
            "args": [[str(fid)], {"frame": {"duration": 100, "redraw": True},
                                  "mode": "immediate"}],
            "label": str(fid),
            "method": "animate",
        } for fid in frames],
        "transition": {"duration": 0},
        "x": 0,
        "y": -0.1,
        "currentvalue": {"prefix": "Frame: "}
    }],
    shapes=[
        # Endzones
        dict(type="rect", x0=0, x1=10, y0=0, y1=FIELD_WIDTH, fillcolor="rgba(0, 0, 255, 0.2)", line_width=0, layer="below"),
        dict(type="rect", x0=110, x1=120, y0=0, y1=FIELD_WIDTH, fillcolor="rgba(255, 0, 0, 0.2)", line_width=0, layer="below"),
    ]
)

def frame_to_traces(frame_data):
    traces = []
    # Jogadores por time
    for club in frame_data["club"].unique():
        sub_df = frame_data[frame_data["club"] == club]
        marker = dict(size=12)
        # Destacar bola com tamanho e cor diferente
        if club == 'football':
            marker = dict(size=18, color='brown', symbol='circle')
        traces.append(go.Scatter(
            x=sub_df["x"], y=sub_df["y"],
            mode="markers+text",
            marker=marker,
            name=club,
            text=[f"{row} <br>Velocidade: {vel:.2f} jardas/s"
                  for row, vel in zip(sub_df["displayName"], sub_df["velocidade"].fillna(0))],
            textposition="top center"
        ))
    # Trajetória da bola (linha)
    bola_frame = frame_data[frame_data['club'] == 'football']
    if not bola_frame.empty:
        traces.append(go.Scatter(
            x=bola_traj[bola_traj['frameId'] <= frame_data['frameId'].max()]['x'],
            y=bola_traj[bola_traj['frameId'] <= frame_data['frameId'].max()]['y'],
            mode='lines',
            line=dict(color='brown', width=3),
            name='Trajetória da bola',
            showlegend=True,
        ))
    return traces

data = frame_to_traces(first_frame)

animation_frames = [
    go.Frame(data=frame_to_traces(play_tracking[play_tracking["frameId"] == fid]), name=str(fid))
    for fid in frames
]

fig = go.Figure(
    data=data,
    layout=layout,
    frames=animation_frames
)

fig.layout.updatemenus = [dict(
    type="buttons",
    showactive=False,
    buttons=[dict(label="Play",
                  method="animate",
                  args=[None, {"frame": {"duration": 100, "redraw": True},
                               "fromcurrent": True,
                               "transition": {"duration": 0}}])]
)]

st.plotly_chart(fig)

# ————————————
# Heatmap de movimentação por posição
st.subheader("📍 Heatmap de Movimentação por Posição")

# Junta tracking com posição dos jogadores
tracking_with_pos = play_tracking.merge(players[['nflId', 'position']], on='nflId', how='left')

posicoes = tracking_with_pos['position'].dropna().unique()
posicao_selecionada = st.selectbox("Selecione a posição para o heatmap", sorted(posicoes))

heatmap_df = tracking_with_pos[tracking_with_pos['position'] == posicao_selecionada]

if not heatmap_df.empty:
    fig_heatmap = px.density_heatmap(
        heatmap_df,
        x="x",
        y="y",
        nbinsx=50,
        nbinsy=25,
        color_continuous_scale='Viridis',
        title=f"Heatmap de movimentação - Posição: {posicao_selecionada}",
        labels={"x": "Jardas (Comprimento)", "y": "Largura do Campo"}
    )
    fig_heatmap.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))
    st.plotly_chart(fig_heatmap)
else:
    st.info(f"Nenhum dado para a posição {posicao_selecionada} nesta jogada.")

# ————————————
# Estatísticas por tipo de jogada (isDropback)
st.subheader("📊 Estatísticas por tipo de jogada (Dropback ou não)")

jogo_plays = team_plays[team_plays['gameId'] == game_id]

if 'isDropback' in jogo_plays.columns:
    team_stats = jogo_plays.groupby('isDropback').agg({
        'yardsToGo': 'mean',
        'yardsGained': 'mean',
        'expectedPointsAdded': 'mean'
    }).rename(columns={
        'yardsToGo': 'Média de Jardas para o 1st Down',
        'yardsGained': 'Jardas Ganhas Médias',
        'expectedPointsAdded': 'EPA Médio'
    })

    team_stats.index = team_stats.index.map({True: 'Passe (Dropback)', False: 'Corrida ou Outra'})
    st.dataframe(team_stats)
else:
    st.info("A coluna `isDropback` não está presente neste dataset.")
