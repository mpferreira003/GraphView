import cv2
import imports
imports.imports()

from generator import MundoPequeno
from navigator import Navigator
from algo import *


n = 100
mp = MundoPequeno(n,seed=42)
mp.create_data(dim=2)
mp.create_connections(3,0.02) ## k=3, p=0.1
connections = mp.get_connections()


## ------------------------------------- #### ------------------------------------- ##

graph = Navigator(allow_gif=True)
for node,conn,dist in connections:
    graph.add(node,conn,weight=dist)

img_dimension = (600,600)
graph.compile(img_dimension,border=-150,kwargs_graph={'k':0.05})
graph.set_attributes(radius=5,radius_add=4,thickness=1,thickness_add=2)


goal = 12
heuristica = lambda x: abs(x - goal)
#heuristica = lambda x: 0

graph.set_goal(goal)
#algo = DFS(graph)
#algo = BFS(graph)
#algo = AEstrela(graph, heuristica)
#algo = BestFirstSearch(graph, heuristica)  # Esse nem sempre acha
algo = HillClimb(graph, heuristica) # Essa heuristica eh muito ruim pro hill climb

res = algo.run(1, goal)
if res:
    print('Achou!')
else:
    print('Nao achou!')

graph.make_gif("Algo")

mostra_grafo(graph, True)
input()

