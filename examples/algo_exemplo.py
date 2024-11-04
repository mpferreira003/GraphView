import cv2
import imports
imports.imports()

from generator import MundoPequeno
from navigator import Navigator
from algoritmos import *
import math

n = 1000
mp = MundoPequeno(n,seed=42)
mp.create_data(dim=2)
mp.create_connections(3,0.02) ## k=3, p=0.1
connections = mp.get_connections()


## ------------------------------------- #### ------------------------------------- ##

graph = Navigator(allow_gif=True)
for node,conn,dist in connections:
    graph.add(node,conn,weight=dist)

img_dimension = (600,600)
graph.compile(img_dimension,
              border=-150,
              kwargs_graph={'k':0.05},
              nodes_positions=mp.embeddings
              )
graph.set_attributes(radius=5,radius_add=4,thickness=1,thickness_add=2)


goal = 10
# heuristica = lambda x: abs(x)
def heuristica_euclidian(outro,goal):
    return math.sqrt((outro[0]-goal[0])**2+(outro[1]-goal[1])**2)
def heuristica_manhattan(atual, goal):
    return abs(goal[0] - atual[0]) + abs(goal[1] - atual[1])
def heuristica_chebyshev(atual, goal):
    return max(abs(goal[0] - atual[0]), abs(goal[1] - atual[1]))


graph.set_goal(goal)


# algo = DFS(graph)
# algo = BFS(graph)
# algo = AEstrela(graph, heuristica_euclidian)
# algo = BestFirstSearch(graph, heuristica)  # Esse nem sempre acha
algo = HillClimb(graph, heuristica_euclidian) # Essa heuristica eh muito ruim pro hill climb

print("Busca iniciada ----")
res = algo.run(1, goal)
if res:
    print('Achou!')
else:
    print('Nao achou!')

if graph.can_plot:
    graph.make_gif("Algo")
else:
    print("A visualização do grafo não está disponível")