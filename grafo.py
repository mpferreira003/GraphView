"""

Este código implementa um grafo visual usando as bibliotecas networkx e opencv.
Ele cria um grafo com nós e arestas, onde cada nó tem uma posição e estado
(ativo ou inativo), e as arestas conectam os nós com um peso.
O estado de nós e arestas pode ser alterado, e a visualização do grafo é feita
com círculos para os nós e linhas para as arestas.
A visualização pode ser modificada para mostrar diferentes estados 
(ativado/desativado) usando cores. 
O grafo pode ser salvo e carregado a partir de um arquivo .pkl.

"""
import networkx as nx
import cv2
import numpy as np
import pickle
from typing import cast


# Soma vetorial de duas triplas de cores
# Se passar de 255 ou de 0, ele conserta o limite
def add_color(color1, color2):
    color3 = np.array(color1, dtype=int) + np.array(color2, dtype=int)
    for i in range(3):
        if color3[i] > 255:
            color3[i] = 255
        elif color3[i] < 0:
            color3[i] = 0
    return color3.tolist()


# Classe que representa um nó no grafo visual
class Node:
    def __init__(self, center_img, center):
        self.center_img = np.array(center_img, dtype=int)  # posição na imagem
        self.center = np.array(center)  # posição no gráfico
        self.activate = False  # Estado inicial (desativado)

    def set_state(self, state: bool):
        self.activate = state  # Altera o estado (ativo ou inativo)

    def set_attributes(self,
                       color_activate,
                       color_deactivate,
                       default_color_append=70,
                       radius=10,
                       radius_add=10):
        self.activate = False  # Começa desativado

        self.radius = radius  # Raio padrão do nó
        self.radius_add = radius_add  # Raio extra quando ativo

        self.color_activate = color_activate  # Cor do nó quando ativado
        self.color_deactivate = color_deactivate  # Cor do nó quando desativado
        self.default_color_append = default_color_append  # Cor adicional para bordas

    def draw(self, img):
        # Desenha o nó na imagem
        if self.activate:
            # Desenha nó ativado com cor de borda
            border_color = add_color(
                self.color_activate, self.default_color_append)
            img = cv2.circle(img, self.center_img, self.radius +
                             self.radius_add, border_color, -1)
            return cv2.circle(img, self.center_img, self.radius, self.color_activate, -1)
        else:
            # Desenha nó desativado com cor padrão
            return cv2.circle(img, self.center_img, self.radius, self.color_deactivate, -1)


# Classe que representa uma aresta entre dois nós no grafo
class Aresta:
    def __init__(self, p1, p2, weight):
        self.p1 = np.array(p1, dtype=int)  # Posição do primeiro nó
        self.p2 = np.array(p2, dtype=int)  # Posição do segundo nó
        self.weight = weight  # Peso da aresta
        self.activate = False  # Estado inicial da aresta (desativada)

    def set_state(self, state: bool):
        self.activate = state  # Altera o estado (ativo ou inativo)
    
    def set_attributes(self,
                       color_activate,
                       color_deactivate,
                       default_color_add=70,
                       thickness=2,
                       thickness_add=3):
        self.activate = False  # Começa desativada

        self.thickness = thickness  # Espessura padrão da linha
        self.thickness_add = thickness_add  # Espessura extra quando ativada

        self.color_activate = color_activate  # Cor da aresta quando ativada
        self.color_deactivate = color_deactivate  # Cor da aresta quando desativada
        self.default_color_add = default_color_add  # Cor adicional para bordas

    def draw(self, img):
        # Desenha a aresta na imagem
        if self.activate:
            # Desenha aresta ativada com cor de borda
            border_color = add_color(
                self.color_activate, self.default_color_add)
            img = cv2.line(img, self.p1, self.p2, border_color,
                           self.thickness + self.thickness_add)
            return cv2.line(img, self.p1, self.p2, self.color_activate, self.thickness)
        else:
            # Desenha aresta desativada com cor padrão
            return cv2.line(img, self.p1, self.p2, self.color_deactivate, self.thickness)


# Classe que representa o grafo visual
class VisualGraph:
    def __init__(self,
                 color_deactivate=(100, 100, 100),
                 color_activate=(0, 0, 200),
                 color_add=70,
                 radius=10,
                 radius_add=10,
                 thickness=2,
                 thickness_add=3) -> None:
        # Atributos de estilo
        self.radius = radius
        self.radius_add = radius_add
        self.thickness = thickness
        self.thickness_add = thickness_add

        self.G = nx.Graph()  # Grafo em si (estrutura de dados)

        # Cores de ativação e desativação
        self.color_deactivate = color_deactivate
        self.color_activate = color_activate
        self.color_add = color_add

        self.connections = {}  # Armazena conexões entre os nós
        self.compilated = False  # Indica se o grafo foi compilado
        self.node_id_mapping = {}  # Mapeamento de IDs dos nós
        self.node_id_antimapping = {}  # Mapeamento inverso de IDs dos nós

    def add(self,
            node: int,
            conn: int,
            weight: float = None):
        """
        Função para adicionar um nó e suas conexões ao grafo.
        """
        node=int(node)
        conn=int(conn)
        # Mapeamento dos nós
        if node in self.node_id_mapping.keys():
            node_id = self.node_id_mapping[node]
        else:
            node_id = len(self.node_id_mapping)
            self.node_id_antimapping[node_id] = node
            self.node_id_mapping[node] = node_id

        # Mapeamento das conexões
        if conn is not None:
            if conn in self.node_id_mapping.keys():
                conn_id = self.node_id_mapping[conn]
            else:
                conn_id = len(self.node_id_mapping)
                
                self.node_id_antimapping[conn_id] = conn
                self.node_id_mapping[conn] = conn_id
            
            self.G.add_edge(node_id, conn_id, weight=weight)  # Adiciona aresta
        else:
            self.G.add_node(node_id)  # Adiciona apenas o nó
        print(f"No {conn} -> mapeamento para: {conn_id}")
        
        # Armazena as conexões para o nó
        if node_id in self.connections.keys():
            self.connections[node_id].append((conn_id, weight))
        else:
            self.connections[node_id] = [(conn_id, weight),]
    
    def compile(self, img_shape: np.ndarray,
                border: int = 30,
                nodes_positions=None,
                kwargs_graph={}):
        """
        Função para compilar a representação visual do grafo, 
        gerando as posições dos nós e arestas.
        """
        self.img_shape = np.array(img_shape)
        
        # Calcula o tamanho da imagem para incluir a borda
        desired_img_shape = self.img_shape - 2*border
        if nodes_positions is None:
            # Calcula posições dos nós
            positions = nx.spring_layout(self.G, **kwargs_graph)
            points = list(positions.values())
            translade = self.img_shape/2  # valor a ser somado em todos os points
        else:
            points = nodes_positions
            translade = np.zeros(2)  # valor a ser somado em todos os points
        
        ## reorganiza os pontos de acordo com o mapeamento inicial
        indexes = [self.node_id_antimapping[i] for i in range(len(points))]
        points = [points[i] for i in indexes]
        
        # Calcula a escala para ajustar os nós na imagem
        min_dims = np.min(points, axis=0)
        max_dims = np.max(points, axis=0)

        graph_height_width = max_dims - min_dims
        # o quanto precisa aumentar para cobrir todo mapa
        scale = (desired_img_shape*1/2) / graph_height_width
        
        def get_imgposition(x, y): 
            return translade+(np.array((x, y)))*scale
        
        # Cria os objetos Node e Aresta
        nodes_positions_in_img = [get_imgposition(x, y) for x, y in points]
        self.nodes = [Node(center, center_real) for center, center_real in list(
            zip(nodes_positions_in_img, points))]
        
        print("batata: ",indexes)
        print("self.nodes: \n",self.nodes)
        
        # Cria as arestas
        self.arestas = {}
        for node_idx, connections in list(self.connections.items()):
            for (conn_idx, weight) in connections:
                # print(f"self.node_id_antimapping[{node_idx}]: ",self.node_id_antimapping[node_idx])
                p1 = nodes_positions_in_img[node_idx]
                p2 = nodes_positions_in_img[conn_idx]
                self.arestas[(node_idx, conn_idx)] = Aresta(p1=p1,
                                                            p2=p2,
                                                            weight=weight)

        # Configura os atributos dos nós e arestas
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
                       radius=None, radius_add=None,
                       thickness=None, thickness_add=None):
        """
        Função para configurar os atributos de estilo do grafo.
        """
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

        # Aplica as configurações para todos os nós
        for node in self.nodes:
            node.set_attributes(
                color_activate,
                color_deactivate,
                default_color_append=color_add,
                radius=radius,
                radius_add=radius_add
            )

        # Aplica as configurações para todas as arestas
        for (i, j), aresta in self.arestas.items():
            aresta.set_attributes(
                color_activate,
                color_deactivate,
                default_color_add=color_add,
                thickness=thickness,
                thickness_add=thickness_add
            )

    def plot(self, step=None):
        """
        Função para plotar o grafo em uma imagem.
        """
        if not self.compilated:
            raise ValueError(
                "Você deve fazer o .compile do grafo antes de chamar o plot")

        img = np.full(
            (self.img_shape[0], self.img_shape[1], 3), 255, dtype='uint8')  # Cria imagem em branco
        for node in self.nodes:
            img = node.draw(img)  # Desenha os nós
        for (i, j), aresta in self.arestas.items():
            img = aresta.draw(img)  # Desenha as arestas

        if step is not None:
            # Adiciona um texto indicando o número da etapa
            img = cv2.putText(img, f'{step}', (30, 30),
                              cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
        return img

    def set_node_state(self, node_id: int, state: bool):
        """
        Função para alterar o estado de um nó.
        """
        if not self.compilated:
            raise ValueError(
                "Você deve fazer o .compile do grafo antes de tentar alterar o estado de algum nó")
        if node_id < len(self.nodes) and node_id >= 0:
            self.nodes[node_id].set_state(state)
            return True
        else:
            return False

    def set_aresta_state(self, node_i: int, node_j: int, state: bool):
        """
        Função para alterar o estado de uma aresta.
        """
        if not self.compilated:
            raise ValueError(
                "Você deve fazer o .compile do grafo antes de tentar alterar o estado de alguma aresta")
        if (node_i, node_j) in self.arestas.keys():
            self.arestas[(node_i, node_j)].set_state(state)
            return True
        else:
            return False

    def save(self, file_name: str):
        """
        Função que salva o grafo visual em um arquivo `.pkl`.
        """
        if not self.compilated:
            file_name += '_uncompilated'
        file_name += '.pkl' if '.pkl' not in file_name else ''
        with open(f"{file_name}", "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load(file_name: str):
        """
        Função que carrega um grafo a partir de um arquivo `.pkl`.
        """
        file_name += '.pkl' if '.pkl' not in file_name else ''
        with open(file_name, "rb") as file:
            file = pickle.load(file)
            return cast(VisualGraph, file)


# Código de execução, onde se define o grafo e chama-se a função de plotagem
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
             (25, 26, 0.88)]  # Conexões e pesos dos nós

    Grafo = VisualGraph()  # Criação do grafo visual
    for node, conn, weight in nodes:
        Grafo.add(node, conn, weight=weight)  # Adiciona nós e arestas

    img_shape = (500, 500, 3)  # Tamanho da imagem
    Grafo.compile(img_shape[:2], border=0)  # Compila o grafo para visualização
    Grafo.set_attributes(
        color_activate=(0, 0, 200),
        color_deactivate=(100, 100, 100),
        color_add=70,
        radius=6,
        radius_add=3,
        thickness=2,
        thickness_add=2
    )

    def plot():
        for i in range(10):
            # Geração de estados aleatórios para os nós
            states = np.random.randint(0, 2, len(Grafo.nodes))
            for j, state in enumerate(states):
                Grafo.set_node_state(j, state)

            # Alteração do estado das arestas
            for j, s_j in enumerate(states):
                for k, s_k in enumerate(states):
                    a = Grafo.set_aresta_state(j, k, s_j and s_k)

            # Plota o grafo
            img = Grafo.plot()
            cv2.imshow('Batata', img)
            cv2.waitKey(500)  # Espera meio segundo

    plot()  # Chama a função de plotagem
