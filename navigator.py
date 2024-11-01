import numpy as np
from grafo import VisualGraph

CONNECTED = True
DISCONNECTED = False

class Navigator(VisualGraph):
    def __init__(self):
        super().__init__()
    def compile(self,img_shape:np.ndarray,
                border:int=30,
                color_activate=None,
                color_deactivate=None,
                color_add=None,
                radius=None,radius_add=None,
                thickness=None,thickness_add=None,
                kwargs_graph={}):
        """
        Compila e seta os atributos
        """
        super().compile(img_shape,
                border=border,kwargs_graph=kwargs_graph)
        super().set_attributes(
                color_deactivate=color_deactivate,
                color_activate=color_activate,
                color_add=color_add,
                radius=radius,
                radius_add=radius_add,
                thickness=thickness,
                thickness_add=thickness_add
                )
        
        
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
        
        if self.nodes[mapped_destination_id].activate:
            return False ## já foi visitado
        
        
        neighboors = self.get_neighboors(current_node_id,return_internal=True)
        print(f"mapped_current_id: {mapped_current_id}  mapped_destination_id:{mapped_destination_id} neighboors:",neighboors)
        if mapped_destination_id in neighboors:
            self.set_aresta_state(mapped_current_id,mapped_destination_id,CONNECTED)
            self.set_node_state(mapped_destination_id,CONNECTED)
            
            print("conseguiu setar aresta: ",self.set_aresta_state(mapped_destination_id,mapped_current_id,CONNECTED))
            print("conseguiu setar o no: ",self.set_node_state(mapped_current_id,CONNECTED))
            return True ## foi possível ir até a localização
        else:
            print("Não foi possível ir até a loc")
            return False ## não foi possível ir até a localização
    def reset(self):
        """
        Volta a rede ao estado inicial
        """
        for node in self.nodes:
            node.set_state(DISCONNECTED)
        for aresta in self.arestas.values():
            aresta.set_state(DISCONNECTED)
        
    

