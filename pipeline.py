from algoritmos import *
from heuristicas import *
import time
import matplotlib.pyplot as plt
import numpy as np

algorithms = {
    "DFS":DFS,
    "BFS":BFS,
    "AEstrela":AEstrela,
    "Dijkstra":Dijkstra,
    "BestFirstSearch":BestFirstSearch,
    "HillClimb":HillClimb
}
heuristicas = {
    "euclidian":heuristica_euclidian,
    "manhattan":heuristica_manhattan,
    "chebyshev":heuristica_chebyshev,
    "None":None
}


def pipeline(mundoPequeno_connections:list,
             algorithm_name:str,
             heuristica_name:str,
             init_node:int,
             goal_node:int,
             gif_name=None,
             nodes_positions=None,
             img_dimension=(600,600),
             try_plot=False,
             kwargs_run={},
             kwargs_gif={}):
    
    ## Fazendo as conexões
    graph = Navigator(allow_gif= gif_name is not None )
    for node,conn,dist in mundoPequeno_connections:
        graph.add(node,conn,weight=dist)
        
    graph.compile(img_dimension,
              border=-150,
              kwargs_graph={'k':0.05},
              nodes_positions=nodes_positions
              )
    
    graph.set_attributes(radius=5,radius_add=4,thickness=1,thickness_add=2)
    graph.set_goal(goal_node)
    
    
    ## algorithm
    heuristica = heuristicas[heuristica_name]
    algorithm_type = algorithms[algorithm_name]
    
    ## realizando o experimento
    ti = time.time()
    algorithm = algorithm_type(graph,heuristica=heuristica)
    conseguiu_chegar = algorithm.run(init_node,goal_node,try_plot=try_plot,**kwargs_run)
    print("conseguiu_chegar: ",conseguiu_chegar)
    tf = time.time()
    
    
    ## salvando os dados
    delay_time = tf-ti
    n = len(graph.node_id_antimapping)
    experiment_name = f'{algorithm_name}_{n}nodes'
    
    if try_plot:
        graph.make_gif(gif_name,**kwargs_gif)
    
    if heuristica is None: ## Se não tiver heurística
        return experiment_name,delay_time,[]
    else:
        return experiment_name,delay_time,algorithm.heuristic_historic

def plot_historic(experiment_name,delay_time,heuristic_historic,ax=None,plt_color='g'):
    title = f"{experiment_name} - {delay_time:.3f}s"
    
    ## dados do gráfico
    plt.title(title)
    plt.xlabel("Number of Steps")
    plt.ylabel("heuristic")
    print('heuristic_historic: ',heuristic_historic)
    y_max_range = np.max(heuristic_historic)+np.std(heuristic_historic)
    Xs = np.arange(len(heuristic_historic))
    if len(Xs)<20: plt.xticks(Xs)
    plt.ylim(0,y_max_range)
    
    
    ## plot da heurística
    
    plt.plot(Xs,heuristic_historic,color=plt_color)
    plt.scatter(Xs,heuristic_historic,color=plt_color)
    
    plt.show()
