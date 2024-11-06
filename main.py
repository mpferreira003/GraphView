from generator import MundoPequeno
from pipeline import *

# ---- cria as conexões
n = 100  # Número de nós do grafo
# Cria um grafo de "mundo pequeno" com 100 nós e uma seed fixa
mp = MundoPequeno(n, seed=42)
mp.create_data(dim=2)  # Gera os dados de posicionamento dos nós no espaço 2D
# Cria as conexões no grafo: k=3 (3 vizinhos mais próximos), p=0.02 (2% de conexões aleatórias)
mp.create_connections(3, 0.02)
# Obtém as conexões geradas, que serão usadas no experimento
connections = mp.get_connections()

# ---- roda o algoritmo
# Chama a função pipeline para rodar o experimento com as conexões geradas
exp_name, delay, historic = pipeline(
    connections,                   # Conexões geradas no mundo pequeno
    'AEstrela',                    # Nome do algoritmo: A* (AEstrela)
    'euclidian',                   # Nome da heurística: Euclidiana
    1,                              # Nó inicial para a busca (nó 1)
    13,                             # Nó objetivo para a busca (nó 13)
    gif_name='batata',             # Nome do arquivo GIF a ser gerado, se try_plot for True
    try_plot=True,                 # Se True, gera o gráfico e o GIF do processo
    # Parâmetros adicionais para o GIF (ajusta o delay entre frames)
    kwargs_gif={'delay_frame': 200},
    # kwargs_run = {'max_it':20}   ## Dá para adicionar parâmetros do algoritmo aqui, como o valor de w no AEstrela
)

# ---- Se a execução do algoritmo tiver gerado histórico da heurística, plota
# Se o histórico de heurísticas for retornado, chama a função para plotar o gráfico da heurística ao longo do processo
if historic:
    plot_historic(exp_name, delay, historic)
