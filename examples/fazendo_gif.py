import cv2
import imports
imports.imports()

from generator import MundoPequeno
from navigator import Navigator


n = 100
mp = MundoPequeno(n,seed=42)
mp.create_data(dim=2)
mp.create_connections(3,0.1) ## k=3, p=0.1
connections = mp.get_connections()


## ------------------------------------- #### ------------------------------------- ##

graph = Navigator(allow_gif=True)
for node,conn,dist in connections:
    graph.add(node,conn,weight=dist)

img_dimension = (600,600)
graph.compile(img_dimension,border=-150,kwargs_graph={'k':0.05})
graph.set_attributes(radius=5,radius_add=4,thickness=1,thickness_add=2)



def dfs(initial_node):
    queue = [initial_node]
    visitados = []
    step = 0
    while len(queue)>0:
        node = queue.pop(0)
        while node in visitados:
            node = queue.pop(0) if len(queue)>0 else None
        if node is None:
            break
        visitados.append(node)
        
        neighboors = graph.get_neighboors(node)
        for neighboor in neighboors:
            graph.nav(node,neighboor)
            queue.insert(0,neighboor)
        img = graph.plot()
        cv2.imshow('Batata',img)
        cv2.waitKey(20)
        step+=1
        


graph.set_goal(12)
dfs(1)
print("dfs terminada")
graph.make_gif("DFS")