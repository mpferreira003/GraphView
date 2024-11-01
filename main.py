from generator import MundoPequeno
from navigator import Navigator
import cv2

n = 100
mp = MundoPequeno(n,seed=42)
mp.create_data(dim=2)
mp.create_connections(3,0.1)
connections = mp.get_connections()


## ------------------------------------- ##


graph = Navigator()
for node,conn,dist in connections:
    graph.add(node,conn,weight=dist)

img_dimension = (600,600)
graph.compile(img_dimension,border=-150,kwargs_graph={'k':0.05})
# graph.save('saves/grafo100nos')
# exit(1)

# graph = Navigator.load('saves/grafo100nos.pkl')
graph.set_attributes(
    radius=5,radius_add=4,
    thickness=1,thickness_add=2,
)
print(graph.connections)
def dfs(initial_node):
    queue = [initial_node]
    step = 0
    while len(queue)>0 and step<20:
        print("queue: ",queue)
        node = queue.pop(0)
        neighboors = graph.get_neighboors(node)
        # print(f"neighboors reais do nó real [{node}]: {neighboors} {[graph.node_id_mapping[nei] for nei in neighboors]}")
        for neighboor in neighboors:
            has_possible = graph.nav(node,neighboor)
            if has_possible:
                queue.insert(0,neighboor)
        img = graph.plot()
        cv2.imshow('Batata',img)
        cv2.waitKey(100)
        step+=1
    print("dfs terminada")

dfs(0)