from algoritmos import *
from heuristicas import *
import time
import matplotlib.pyplot as plt
import numpy as np

# Dicionário de algoritmos de busca disponíveis
algorithms = {
    "DFS": DFS,                # Busca em Profundidade
    "BFS": BFS,                # Busca em Largura
    "AEstrela": AEstrela,      # Algoritmo A*
    "Dijkstra": Dijkstra,      # Algoritmo de Dijkstra
    "BestFirstSearch": BestFirstSearch,  # Busca Best-First
    "HillClimb": HillClimb     # Algoritmo de Hill Climbing
}

# Dicionário de heurísticas disponíveis
heuristicas = {
    "euclidian": heuristica_euclidian,     # Heurística Euclidiana
    "manhattan": heuristica_manhattan,     # Heurística Manhattan
    "chebyshev": heuristica_chebyshev,     # Heurística Chebyshev
    "None": None                          # Sem heurística
}


def pipeline(mundoPequeno_connections: list,
             algorithm_name: str,
             heuristica_name: str,
             init_node: int,
             goal_node: int,
             gif_name=None,
             nodes_positions=None,
             img_dimension=(600, 600),
             try_plot=False,
             kwargs_run={},
             kwargs_gif={}):
    """
    Função principal que executa um experimento com um algoritmo de busca no grafo de pequeno mundo.
    Conecta os nós, escolhe o algoritmo e heurística, executa a busca e gera o resultado.

    Args:
        mundoPequeno_connections: list - Lista com as conexões entre os nós e suas distâncias.
        algorithm_name: str - Nome do algoritmo de busca a ser utilizado.
        heuristica_name: str - Nome da heurística a ser utilizada.
        init_node: int - Nó de início para a busca.
        goal_node: int - Nó objetivo para a busca.
        gif_name: str (opcional) - Nome do arquivo para salvar um gif do processo.
        nodes_positions: list (opcional) - Posições dos nós para visualização.
        img_dimension: tuple - Dimensões da imagem de visualização.
        try_plot: bool - Se True, gera gráficos e gif do processo.
        kwargs_run: dict - Argumentos adicionais para o algoritmo de busca.
        kwargs_gif: dict - Argumentos adicionais para a geração do gif.

    Returns:
        tuple - Nome do experimento, tempo de execução e histórico da heurística (se houver).
    """

    # Criando o grafo e adicionando as conexões
    graph = Navigator(allow_gif=gif_name is not None)
    for node, conn, dist in mundoPequeno_connections:
        graph.add(node, conn, weight=dist)

    # Configurações do gráfico e posições dos nós
    graph.compile(img_dimension,
                  border=-150,
                  kwargs_graph={'k': 0.05},
                  nodes_positions=nodes_positions)
    graph.set_attributes(radius=5, radius_add=4, thickness=1, thickness_add=2)
    graph.set_goal(goal_node)

    # Seleciona a heurística e o algoritmo a serem utilizados
    heuristica = heuristicas[heuristica_name]
    algorithm_type = algorithms[algorithm_name]

    # Início da execução do algoritmo
    ti = time.time()  # Marca o tempo de início
    algorithm = algorithm_type(graph, heuristica=heuristica)
    conseguiu_chegar = algorithm.run(
        init_node, goal_node, try_plot=try_plot, **kwargs_run)
    tf = time.time()  # Marca o tempo de término

    # Exibe se o algoritmo conseguiu chegar ao objetivo
    print("conseguiu_chegar: ", conseguiu_chegar)

    # Calcula o tempo total de execução
    delay_time = tf - ti
    n = len(graph.node_id_antimapping)  # Número de nós no grafo
    experiment_name = f'{algorithm_name}_{n}nodes'

    # Se o parâmetro try_plot for True, gera o gif do processo
    if try_plot:
        graph.make_gif(gif_name, **kwargs_gif)

    # Se não houver heurística, retorna apenas o nome do experimento e o tempo
    if heuristica is None:
        return experiment_name, delay_time, []
    else:
        # Caso contrário, retorna também o histórico da heurística
        return experiment_name, delay_time, algorithm.heuristic_historic


def plot_historic(experiment_name, delay_time, heuristic_historic, ax=None, plt_color='g'):
    """
    Função que plota o histórico da heurística durante o processo de busca.

    Args:
        experiment_name: str - Nome do experimento.
        delay_time: float - Tempo total de execução.
        heuristic_historic: list - Histórico dos valores da heurística durante a busca.
        ax: Axes (opcional) - Eixos do gráfico para plotar.
        plt_color: str - Cor da linha do gráfico.
    """
    title = f"{experiment_name} - {delay_time:.3f}s"

    # Dados do gráfico
    plt.title(title)
    plt.xlabel("Number of Steps")
    plt.ylabel("heuristic")

    # Calcula o intervalo do eixo y com base no valor máximo da heurística e seu desvio padrão
    y_max_range = np.max(heuristic_historic) + np.std(heuristic_historic)
    Xs = np.arange(len(heuristic_historic))  # Passos da busca
    if len(Xs) < 20:
        plt.xticks(Xs)
    plt.ylim(0, y_max_range)

    # Plota a heurística ao longo dos passos
    plt.plot(Xs, heuristic_historic, color=plt_color)
    plt.scatter(Xs, heuristic_historic, color=plt_color)

    # Exibe o gráfico
    plt.show()
