import numpy as np
from grafo import VisualGraph
# from pil import Image
from PIL import Image
import cv2
import os

CONNECTED = True
DISCONNECTED = False

class Navigator(VisualGraph):
    def __init__(self,allow_gif=False):
        self.allow_gif=allow_gif
        self.gif_images = []
        super().__init__()
    def compile(self,img_shape:np.ndarray,
                border:int=30,
                color_activate=None,
                color_deactivate=None,
                color_add=None,
                radius=None,radius_add=None,
                thickness=None,thickness_add=None,
                kwargs_graph={},nodes_positions=None):
        """
        Compila e seta os atributos
        """
        super().compile(img_shape,
                border=border,kwargs_graph=kwargs_graph,nodes_positions=nodes_positions)
        
        super().set_attributes(
                color_deactivate=color_deactivate,
                color_activate=color_activate,
                color_add=color_add,
                radius=radius,
                radius_add=radius_add,
                thickness=thickness,
                thickness_add=thickness_add
                )
        self.goal=None
        self.allow_gif = self.allow_gif
    def get_neighboors(self,current_node_id:int,current_is_internal=False,return_internal=False):
        if current_is_internal:
            mapped_current_id = current_is_internal
        else:
            mapped_current_id = self.node_id_mapping[current_node_id]
        
        neighboors = self.connections[mapped_current_id]
        neighboors = [neighboor[0] for neighboor in neighboors]
        
        if not return_internal:
            neighboors = [int(self.node_id_antimapping[neighboor]) for neighboor in neighboors]
        return neighboors
    def nav(self,current_node_id:int,destination_id:int):
        """
        Recebe um nó e tenta ir até ele. É necessário
        ter chamado o compile antes de usar esta função
        Args:
            current_node_id:int - id do nó de onde você saiu para chegar 
                no destination
            destination_id:int - id do nó para ir. O mapping
                é passado em cima dele
        Returns:
            :bool - se foi possível ir até a localização ou não
        """
        ## etapa de mapeamento para id interno da rede
        mapped_destination_id = self.node_id_mapping[destination_id]
        mapped_current_id = self.node_id_mapping[current_node_id]

        
        neighboors = self.get_neighboors(current_node_id,return_internal=True)
        
        if mapped_destination_id in neighboors:
            conseguiu_setar = self.set_aresta_state(mapped_current_id,mapped_destination_id,CONNECTED)
            self.set_node_state(mapped_destination_id,CONNECTED)
            chegou_no_goal = destination_id == self.goal if self.goal is not None else False  ## retorna se o goal foi atingido
            return chegou_no_goal
        else:
            raise ValueError("Ok, provavelmente deu algum erro. O nó de destino não está entre os vizinhos do nó inicial")
        
    def add_imgtogif(self):
        if self.allow_gif:
            self.gif_images.append(self.plot(len(self.gif_images)))
    def undo_nav(self,current_node_id:int,destination_id:int):
        """
        Desfaz uma ação que já foi feita de navegação
        Args:
            current_node_id:int - id do nó de onde você saiu para chegar 
                no destination
            destination_id:int - id do nó para ir. O mapping
                é passado em cima dele
        Returns:
            :bool - se foi possível ir até a localização ou não
        """
        mapped_destination_id = self.node_id_mapping[destination_id]
        mapped_current_id = self.node_id_mapping[current_node_id]
        if self.nodes[mapped_destination_id].activate:
            return False ## já foi visitado
        
        
        neighboors = self.get_neighboors(current_node_id,return_internal=True)
        print(f"mapped_current_id: {mapped_current_id}  mapped_destination_id:{mapped_destination_id} neighboors:",neighboors)
        if mapped_destination_id in neighboors:
            self.set_aresta_state(mapped_current_id,mapped_destination_id,DISCONNECTED)
            self.set_node_state(mapped_destination_id,DISCONNECTED)
            
            # print("conseguiu setar aresta: ",self.set_aresta_state(mapped_destination_id,mapped_current_id,DISCONNECTED))
            # print("conseguiu setar o no: ",self.set_node_state(mapped_current_id,DISCONNECTED))
            return True ## foi possível ir até a localização
        else:
            print("Não foi possível ir até a loc")
            return False ## não foi possível ir até a localização    
    
    def set_goal(self,node_id:int,color=(0,200,200),color_add=70):
        """
        Função para alterar os atributos do goal
        Args:
            node_id:int - id externo do nó que vira Goal
        """
        print(f"Goal setado para {node_id}")
        internal_node_id = self.node_id_mapping[node_id]
        self.goal = internal_node_id
        self.goal_xy = self.nodes[internal_node_id].center
        self.nodes[internal_node_id].color_activate = color
        self.nodes[internal_node_id].default_color_append = color_add
        self.nodes[internal_node_id].activate = True
    
    def make_gif(self,output_name:str,delay_frame:int=100):
        """
        Função para gerar um gif do grafo
        Args:
            output_name:str - nome do .gif que ficará salvo na pasta saves/
            delay_frame:int [default = 100] - tempo por frame em milissegundos
        """
        if not self.allow_gif:
            raise ValueError("Você não habilitou a gravação 'allow_gif'")
        print("quantidade de imagens: ",len(self.gif_images))
        pil_images = [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in self.gif_images]
        
        
        ## Prevenção para caso o gif não esteja funcionando
        # output_dir = 'saves'
        # output_path = os.path.join(output_dir, 'Algo.gif')
        # os.makedirs(output_dir, exist_ok=True)
        
        
        # Salva como GIF
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
        for node in self.nodes:
            node.set_state(DISCONNECTED)
        for aresta in self.arestas.values():
            aresta.set_state(DISCONNECTED)
        
    def get_pos(self,node_id:int):
        """
        Retorna a posição xy de um nó
        Args:
            node_id:int - id externo do nó (será feito mapping)
        Returns:
            tuple - posição x,y do nó
        """
        internal_node_id = self.node_id_mapping[node_id]
        return self.nodes[internal_node_id].center
    def get_pos_goal(self):
        return self.goal_xy
        
