"""
Este módulo define a classe `Navigator`, que herda de `VisualGraph` e fornece 
funcionalidades para navegação e manipulação de grafos.

A classe `Navigator` foi projetada para simular o processo de navegação em um 
grafo, onde cada nó pode ser ativado ou desativado, e as arestas entre os nós 
podem ser conectadas ou desconectadas. Ela oferece funcionalidades como:
- Navegação entre nós (método `nav`).
- Desfazer navegação (método `undo_nav`).
- Definir um objetivo de navegação (método `set_goal`).
- Compilação e configuração de atributos visuais do grafo (método `compile`).
- Geração de GIFs para visualização da navegação ao longo do tempo (métodos 
  `add_imgtogif` e `make_gif`).
- Resetar o grafo ao seu estado inicial (método `reset`).

Além disso, a classe oferece métodos auxiliares para obter informações sobre a 
posição dos nós no espaço 2D (`get_pos` e `get_pos_goal`), bem como para acessar 
e modificar os vizinhos de um nó (`get_neighboors`).

A navegação é baseada na atualização do estado das arestas e dos nós. Ao mover-se 
entre dois nós, a aresta correspondente é marcada como "conectada", e o nó de 
destino é ativado. O objetivo é atingido quando o nó de destino é alcançado. A 
classe também permite desfazer a navegação e reverter o estado do grafo.

O código depende de bibliotecas externas como `numpy`, `PIL` e `cv2` para 
manipulação de imagens e geração de GIFs.

A principal utilização da classe é permitir a visualização e simulação de 
algoritmos de navegação em grafos, com a possibilidade de gerar animações do 
processo de navegação em formato GIF.
"""


import numpy as np
import math
from grafo import VisualGraph
from PIL import Image
import cv2

# Definição de constantes para os estados de conexão
CONNECTED = True
DISCONNECTED = False


class Navigator(VisualGraph):
    def __init__(self, allow_gif=False):
        # Inicializa a classe com a possibilidade de gerar GIFs
        self.allow_gif = allow_gif
        self.gif_images = []  # Lista para armazenar imagens para o GIF
        super().__init__()  # Chama o construtor da classe base VisualGraph
        self.steps_percorridas = 0
    def compile(self, img_shape: np.ndarray,
                border: int = 30,
                color_activate=None,
                color_deactivate=None,
                color_add=None,
                radius=None, radius_add=None,
                thickness=None, thickness_add=None,
                kwargs_graph={}, nodes_positions=None):
        """
        Compila e seta os atributos do grafo
        """
        # Chama o método compile da classe base para configurar o grafo
        super().compile(img_shape,
                        border=border, kwargs_graph=kwargs_graph, nodes_positions=nodes_positions)

        # Define os atributos de ativação e desativação
        super().set_attributes(
            color_deactivate=color_deactivate,
            color_activate=color_activate,
            color_add=color_add,
            radius=radius,
            radius_add=radius_add,
            thickness=thickness,
            thickness_add=thickness_add
        )
        self.goal = None  # Inicializa a variável de objetivo (goal)
        self.allow_gif = self.allow_gif  # Mantém a configuração do GIF
        self.distancia_percorrida = 0    # coloca a distância percorrida
    def get_neighboors(self, current_node_id: int, current_is_internal=False, return_internal=False, return_weight=False):
        # Função para obter os vizinhos de um nó
        if current_is_internal:
            mapped_current_id = current_is_internal
        else:
            mapped_current_id = self.node_id_mapping[current_node_id]
        
        # Obtém os vizinhos do nó atual
        neighboors = self.connections[mapped_current_id]
        neighboors = [neighboor[0] for neighboor in neighboors]
        
        # Mapeia os vizinhos de volta para os ids externos, se necessário
        if not return_internal:
            neighboors = [int(self.node_id_antimapping[neighboor])
                          for neighboor in neighboors]
        
        # Se for necessário, retorna os pesos das arestas entre os nós
        if return_weight:
            x, y = self.get_pos(current_node_id)
            def dist(par): return math.sqrt((par[0]-x)**2 + (par[1]-y)**2)
            
            return [(idx, dist(self.get_pos(idx))) for idx in neighboors]
        else:
            return neighboors
            

    def nav(self, current_node_id: int, destination_id: int):
        """
        Recebe um nó e tenta ir até ele. É necessário
        ter chamado o compile antes de usar esta função
        """
        # Etapa de mapeamento para id interno da rede
        mapped_destination_id = self.node_id_mapping[destination_id]
        mapped_current_id = self.node_id_mapping[current_node_id]
        
        # Obtém os vizinhos do nó atual
        neighboors = self.get_neighboors(current_node_id, return_internal=True)
        
        # Verifica se o destino está entre os vizinhos
        if mapped_destination_id in neighboors:
            # Marca a aresta como conectada e o nó de destino como ativado
            conseguiu_setar = self.set_aresta_state(
                mapped_current_id, mapped_destination_id, CONNECTED)
            self.set_node_state(mapped_destination_id, CONNECTED)
            # Verifica se o objetivo foi atingido
            chegou_no_goal = destination_id == self.goal if self.goal is not None else False
            
            # acumula a distancia percorrida:
            self.distancia_percorrida+=self.arestas[(mapped_current_id,mapped_destination_id)].weight
            self.steps_percorridas += 1
            return chegou_no_goal
        else:
            # Caso o destino não esteja entre os vizinhos
            raise ValueError(
                "Ok, provavelmente deu algum erro. O nó de destino não está entre os vizinhos do nó inicial")
    
    def get_distancia_percorrida(self):
        return self.distancia_percorrida
    def add_imgtogif(self):
        # Adiciona a imagem atual ao GIF se a opção permitir
        if self.allow_gif:
            self.gif_images.append(self.plot(len(self.gif_images)))

    def undo_nav(self, current_node_id: int, destination_id: int):
        """
        Desfaz uma ação que já foi feita de navegação
        """
        # Mapeia os ids externos para os internos
        mapped_destination_id = self.node_id_mapping[destination_id]
        mapped_current_id = self.node_id_mapping[current_node_id]

        # Verifica se o nó de destino já foi ativado (já foi visitado)
        if self.nodes[mapped_destination_id].activate:
            return False  # Não é possível desfazer se o nó foi ativado

        # Obtém os vizinhos do nó atual
        neighboors = self.get_neighboors(current_node_id, return_internal=True)
        print(
            f"mapped_current_id: {mapped_current_id}  mapped_destination_id:{mapped_destination_id} neighboors:", neighboors)

        # Se o destino está entre os vizinhos, desconecta a aresta e desativa o nó de destino
        if mapped_destination_id in neighboors:
            self.set_aresta_state(
                mapped_current_id, mapped_destination_id, DISCONNECTED)
            self.set_node_state(mapped_destination_id, DISCONNECTED)

            return True  # Foi possível desfazer a navegação
        else:
            print("Não foi possível ir até a loc")
            return False  # Não foi possível desfazer a navegação

    def set_goal(self, node_id: int, color=(0, 200, 200), color_add=70):
        """
        Função para alterar os atributos do goal
        """
        print(f"Goal setado para {node_id}")
        # Mapeia o id externo do nó para o id interno
        internal_node_id = self.node_id_mapping[node_id]
        self.goal = internal_node_id  # Define o nó como objetivo
        # Salva a posição do objetivo
        self.goal_xy = self.nodes[internal_node_id].center
        # Altera a cor do nó de objetivo
        self.nodes[internal_node_id].color_activate = color
        self.nodes[internal_node_id].default_color_append = color_add
        self.nodes[internal_node_id].activate = True  # Ativa o nó de objetivo

    def make_gif(self, output_name: str, delay_frame: int = 100):
        """
        Função para gerar um gif do grafo
        """
        if not self.allow_gif:
            raise ValueError("Você não habilitou a gravação 'allow_gif'")

        # Converte as imagens em um GIF
        print("quantidade de imagens: ", len(self.gif_images))
        pil_images = [Image.fromarray(cv2.cvtColor(
            img, cv2.COLOR_BGR2RGB)) for img in self.gif_images]

        # Salva como GIF na pasta 'saves/'
        pil_images[0].save(
            f'saves/{output_name}.gif',
            save_all=True,
            append_images=pil_images[1:],
            optimize=False,
            duration=delay_frame,   # Duração de cada quadro em milissegundos
            loop=0                  # Loop infinito (0 significa loop contínuo)
        )

    def reset(self):
        """
        Volta a rede ao estado inicial
        """
        # Desativa todos os nós e desconecta todas as arestas
        for node in self.nodes:
            node.set_state(DISCONNECTED)
        for aresta in self.arestas.values():
            aresta.set_state(DISCONNECTED)
        
        # reseta a distância percorrida
        self.distancia_percorrida=0
        self.steps_percorridas=0
    def get_pos(self, node_id: int):
        """
        Retorna a posição xy de um nó
        """
        internal_node_id = self.node_id_mapping[node_id]
        return self.nodes[internal_node_id].center

    def get_pos_goal(self):
        return self.goal_xy
