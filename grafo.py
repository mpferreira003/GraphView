import networkx as nx
import cv2
import numpy as np
import pickle 
from typing import cast

def add_color(color1,color2):
    color3 = np.array(color1,dtype=int) + np.array(color2,dtype=int)
    for i in range(3):
        if color3[i]>255:
            color3[i]=255
        elif color3[i]<0:
            color3[i]=0
    return color3.tolist()


class Node:
    def __init__(self,center):
        self.center=np.array(center,dtype=int)
        self.activate = False
    def set_state(self,state:bool):
        self.activate=state
    def set_attributes(self,
                 color_activate,
                 color_deactivate,
                 default_color_append=70,
                 radius=10,
                 radius_add=10):
        self.activate = False ## começa desativado
        
        self.radius = radius ## raio padrão
        self.radius_add = radius_add ## raio que aumenta quando é selecionado
        
        self.color_activate=color_activate
        self.color_deactivate=color_deactivate
        self.default_color_append=default_color_append    
    def draw(self,img):
        if self.activate:
            border_color = add_color(self.color_activate,self.default_color_append)
            img = cv2.circle(img,self.center,self.radius+self.radius_add,border_color,-1)
            return cv2.circle(img,self.center,self.radius,self.color_activate,-1)
        else:
            return cv2.circle(img,self.center,self.radius,self.color_deactivate,-1)

class Aresta:
    def __init__(self,p1,p2,weight):
        self.p1=np.array(p1,dtype=int)
        self.p2=np.array(p2,dtype=int)
        self.weight=weight
        self.activate = False
    def set_state(self,state:bool):
        self.activate=state
    def set_attributes(self,
                 color_activate,
                 color_deactivate,
                 default_color_add=70,
                 thickness=2,
                 thickness_add=3
                 ):
        self.activate = False ## começa desativado
        
        self.thickness = thickness
        self.thickness_add = thickness_add
        
        self.color_activate=color_activate
        self.color_deactivate=color_deactivate
        self.default_color_add=default_color_add    
    def draw(self,img):
        if self.activate:
            border_color = add_color(self.color_activate,self.default_color_add)
            img = cv2.line(img,self.p1,self.p2,border_color,self.thickness+self.thickness_add)
            return cv2.line(img,self.p1,self.p2,self.color_activate,self.thickness)
        else:
            return cv2.line(img,self.p1,self.p2,self.color_deactivate,self.thickness)

class VisualGraph:
    def __init__(self,
                 color_deactivate=(100,100,100),
                 color_activate=(0,0,200),
                 color_add=70,
                 radius=10,
                 radius_add=10,
                 thickness=2,
                 thickness_add=3) -> None:
        
        self.radius=radius
        self.radius_add=radius_add
        self.thickness=thickness
        self.thickness_add=thickness_add
        
        self.G = nx.Graph()
        
        self.color_deactivate = color_deactivate
        self.color_activate = color_activate
        self.color_add = color_add
        
        self.connections = {}
        self.compilated = False ## diz que ainda não foi compilado
        self.node_id_mapping = {}
        self.node_id_antimapping = {}
    def add(self,
            node:int,
            conn:int,
            weight:float=None):
        """
        Função para adicionar apenas um nó
        Args:
            node:int - id do nó a ser adicionado
            connection:int - id do nó conectado a ele. É possível passar este
                parâmetro como None, fazendo com que apenas seja adicionado o nó na rede
            weight:float [default = None] - peso da connection.
        """
        
        ## realiza o mapping do nó
        if node in self.node_id_mapping.keys():
            node_id = self.node_id_mapping[node]
        else:
            node_id = len(self.node_id_mapping)
            self.node_id_antimapping[node_id] = node
            self.node_id_mapping[node] = node_id
            
            
            
        ## realiza o mapping do connection
        if conn is not None:
            if conn in self.node_id_mapping.keys():
                conn_id = self.node_id_mapping[conn]
            else:
                conn_id = len(self.node_id_mapping)
                self.node_id_antimapping[conn_id] = conn
                self.node_id_mapping[conn] = conn_id
        
            self.G.add_edge(node_id,conn_id,weight=weight)    
        else:
            self.G.add_node(node_id)
        
        
        if node_id in self.connections.keys():
            self.connections[node_id].append((conn_id,weight))
        else:
            self.connections[node_id] = [(conn_id,weight),]
    
    def compile(self,img_shape:np.ndarray,
                border:int=30,
                nodes_positions=None,
                kwargs_graph={}):
        """
        Args:
            img_shape:np.ndarray - shape da imagem que você vai plotar
            border:int - tamanhdo da borda da imagem
        
        Função que deve ser chamada depois de colocar todos os nós. 
        Ela cria os objetos do tipo Node e Aresta para guardar, salvando
        as posições calculadas deles
        """
        
        self.img_shape = np.array(img_shape)
        translade = self.img_shape/2 ## valor a ser somado em todos os points
        
        desired_img_shape = self.img_shape - 2*border ## retira como se estivesse tirando os 4 cantos
        
        if nodes_positions is None:
            positions = nx.spring_layout(self.G,**kwargs_graph)
            points = list(positions.values())
        else:
            points = nodes_positions
        
        
        
        min_dims = np.min(points,axis=0)
        max_dims = np.max(points,axis=0)
        
        graph_height_width  = max_dims - min_dims
        scale = (desired_img_shape*1/2) / graph_height_width ## o quanto precisa aumentar para cobrir todo mapa
        
        get_imgposition = lambda x,y: translade+(np.array((x,y)))*scale
        
        ## cria os nos e as arestas
        nodes_positions_in_img = [get_imgposition(x,y) for x,y in points]
        self.nodes = [Node(center) for center in nodes_positions_in_img]
        
        self.arestas = {} ## relaciona nós i,j através de uma aresta
        for node_idx,connections in list(self.connections.items()):
            for (conn_idx,weight) in connections:
                self.arestas[(node_idx,conn_idx)] = Aresta(p1=nodes_positions_in_img[node_idx],
                                        p2=nodes_positions_in_img[conn_idx],
                                        weight=weight)
        
        self.set_attributes(self.color_activate,
                            self.color_deactivate,
                            self.color_add,
                            self.radius,
                            self.radius_add,
                            self.thickness,
                            self.thickness_add)
        self.compilated = True
    def set_attributes(self,
                       color_activate=None,
                       color_deactivate=None,
                       color_add=None,
                       radius=None,radius_add=None,
                       thickness=None,thickness_add=None):
        if color_activate is None:
            color_activate = self.color_activate
        if color_deactivate is None:
            color_deactivate = self.color_deactivate
        if color_add is None:
            color_add = self.color_add
        if radius is None:
            radius = self.radius
        if radius_add is None:
            radius_add = self.radius_add
        
        for node in self.nodes:
            node.set_attributes(
                    color_activate,
                    color_deactivate,
                    default_color_append=color_add,
                    radius=radius,
                    radius_add=radius_add
                    )
        
        for (i,j),aresta in self.arestas.items():
            aresta.set_attributes(
                 color_activate,
                 color_deactivate,
                 default_color_add=color_add,
                 thickness=thickness,
                 thickness_add=thickness_add
                 )
    def plot(self):
        if not self.compilated:
            raise ValueError("Você deve fazer o .compile do grafo antes de chamar o plot")
        
        img = np.full((self.img_shape[0],self.img_shape[1],3),255,dtype='uint8')
        for node in self.nodes:
            img = node.draw(img)
        for (i,j),aresta in self.arestas.items():
            img = aresta.draw(img)
        
        return img
    
    def set_node_state(self,node_id:int,state:bool):
        """
        Função para alterar o estado de um nó
            False - desativado (cor padrão)
            True - ativo (cor ativada)
        
        Args:
            node_id:int - nó a ter o estado alterado
            state:bool - estado ao qual será alterado
        Return:
            :bool - se foi possível realizar a ação ou não
        """
        if not self.compilated:
            raise ValueError("Você deve fazer o .compile do grafo antes de tentar alterar o estado de algum nó")
        if node_id < len(self.nodes) and node_id>=0:
            self.nodes[node_id].set_state(state)
            return True
        else:
            return False
    def set_aresta_state(self,node_i:int,node_j:int,state:bool):
        """
        Função para alterar o estado de uma aresta
            False - desativado (cor padrão)
            True - ativo (cor ativada)
        
        Args:
            node_i:int - índice do nó i
            node_j:int - índice do nó j
            state:bool - estado ao qual será alterado
        Return:
            :bool - se foi possível realizar a ação ou não
        """
        if not self.compilated:
            raise ValueError("Você deve fazer o .compile do grafo antes de tentar alterar o estado de alguma aresta")
        if (node_i,node_j) in self.arestas.keys():
            self.arestas[(node_i,node_j)].set_state(state)
            return True
        else:
            return False

    
    def save(self,file_name:str):
        """
        Função que permite salvar o grafo de pequeno mundo gerado
        em um arquivo .pkl
        Args:
            file_name:str - nome do grafo a ser salvo
        """
        
        
        if not self.compilated:
            file_name += '_uncompilated'
        file_name += '.pkl' if '.pkl' not in file_name else ''
        with open(f"{file_name}", "wb") as file:
            pickle.dump(self, file)
    
    @staticmethod
    def load(file_name:str):
        """
        Método estático que permite abrir um grafo.pkl
        Args:
            file_name:str - nome do arquivo
        Returns:
            :MundoPequeno - objeto do grafo do arquivo
        """
        file_name += '.pkl' if '.pkl' not in file_name else ''
        with open(file_name, "rb") as file:
            file = pickle.load(file)
            return cast(VisualGraph,file)




if __name__ == "__main__":
    nodes = [(0, 6, 0.75),
    (0, 19, 1.21),
    (0, 25, 1.79),
    (0, 26, 0.27),
    (0, 28, 0.99),
    (1, 13, 1.1),
    (1, 26, 0.47),
    (1, 29, 0.72),
    (2, 6, 1.91),
    (3, 19, 0.4),
    (6, 15, 0.74),
    (6, 20, 1.71),
    (6, 23, 0.39),
    (6, 26, 1.19),
    (8, 11, 1.01),
    (9, 10, 1.1),
    (9, 16, 0.63),
    (9, 19, 1.09),
    (9, 21, 0.47),
    (11, 20, 1.41),
    (11, 28, 0.2),
    (13, 15, 1.03),
    (14, 17, 0.47),
    (14, 29, 0.43),
    (15, 20, 0.12),
    (15, 21, 0.61),
    (15, 22, 0.49),
    (15, 25, 1.5),
    (15, 26, 1.32),
    (16, 22, 1.32),
    (16, 26, 0.83),
    (17, 19, 1.19),
    (21, 28, 0.11),
    (22, 26, 0.68),
    (25, 26, 0.88)]

    
    Grafo = VisualGraph()
    for node,conn,weight in nodes:
        Grafo.add(node,conn,weight=weight)


    img_shape = (500,500,3)
    Grafo.compile(img_shape[:2],border=0)
    Grafo.set_attributes(
        color_activate=(0,0,200),
        color_deactivate=(100,100,100),
        color_add=70,
        radius=6,
        radius_add=3,
        thickness=2,
        thickness_add=2
        
    )

    def plot():
        for i in range(10):
            states = np.random.randint(0,2,len(Grafo.nodes))
            for j,state in enumerate(states):
                Grafo.set_node_state(j,state)
            
            for j,s_j in enumerate(states):
                for k,s_k in enumerate(states):
                    a = Grafo.set_aresta_state(j,k,s_j and s_k)
            
            
            img = Grafo.plot()
            cv2.imshow('Batata',img)
            cv2.waitKey(500)
        
    plot()