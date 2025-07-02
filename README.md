# NFL Big Data Bowl Dashboard

Este projeto é um dashboard interativo para visualização e análise dos dados do NFL Big Data Bowl. Permite explorar jogadas, visualizar movimentação dos jogadores e da bola em campo, analisar velocidades, trajetórias e heatmaps por posição.

---

## Funcionalidades

- Visualização animada da movimentação dos jogadores e da bola durante uma jogada
- Cálculo e exibição da velocidade dos jogadores em cada frame
- Heatmap de movimentação filtrado por posição (ex: WR, RB)
- Estatísticas resumidas por tipo de jogada (passe, corrida, etc)
- Campo estilizado com endzones destacadas

---

## Integrantes

- Arthur
- Kauan
- Otavio

---

## Requisitos

- Python 3.10 ou superior
- Pacotes Python listados no `requirements.txt`

---

## Como instalar

1. Clone o repositório

2. Crie e ative um ambiente virtual (opcional, mas recomendado):

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Como rodar

Execute o dashboard com:

```bash
streamlit run app.py
```

Isso abrirá o dashboard no navegador padrão, onde você poderá explorar os dados interativamente.

---

## Estrutura dos arquivos

- `app.py` — código principal do dashboard
- `requirements.txt` — dependências do Python
- `data/` — diretório onde devem ficar os arquivos Parquet com os dados NFL

---

## Referências

- [Streamlit](https://streamlit.io/)
- [NFL Big Data Bowl Dataset](https://www.kaggle.com/c/nfl-big-data-bowl/data)
- [Plotly Python](https://plotly.com/python/)
