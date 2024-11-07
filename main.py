from generator import MundoPequeno
from pipeline import *

# ---- cria as conexões
n = 50  # Número de nós do grafo
# Cria um grafo de "mundo pequeno" com 100 nós e uma seed fixa
mp = MundoPequeno(n, seed=42)
mp.create_data(dim=2)  # Gera os dados de posicionamento dos nós no espaço 2D
# Cria as conexões no grafo: k=2 (2 vizinhos mais próximos), p=0.02 (2% de conexões aleatórias)
mp.create_connections(2, 0.02)
# Obtém as conexões geradas, que serão usadas no experimento
connections = mp.get_connections()

# ---- roda o algoritmo
# Chama a função pipeline para rodar o experimento com as conexões geradas
exp,delay,dist,chegou,steps,hist = pipeline(
    connections,                   # Conexões geradas no mundo pequeno
    'BestFirst',                   # Nome do algoritmo: BestFirst
    'euclidian',                   # Nome da heurística: Euclidiana
    1,                             # Nó inicial para a busca (nó 1)
    20,                            # Nó objetivo para a busca (nó 20)
    gif_name='BestFirst exemplo',  # Nome do arquivo GIF a ser gerado, se try_plot for True
    try_plot=True,                 # Se True, gera o gráfico e o GIF do processo
    nodes_positions=mp.embeddings,
    # Parâmetros adicionais para o GIF (ajusta o delay entre frames)
    kwargs_gif={'delay_frame': 300},
    # kwargs_run = {'w':2}   ## Dá para adicionar parâmetros do algoritmo aqui, como o valor de w no AEstrela
)

# ---- Se a execução do algoritmo tiver gerado histórico da heurística, plota
# Se o histórico de heurísticas for retornado, chama a função para plotar o gráfico da heurística ao longo do processo
if hist:
    plot_historic(hist)
