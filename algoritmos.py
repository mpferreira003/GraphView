import cv2
import time
from navigator import Navigator
from queue import Queue, PriorityQueue 
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)


TIME_PER_IT = 0.1
# TIME_PER_IT = 0

def mostra_grafo(grafo: Navigator, last=False):
    grafo.add_imgtogif()

class DFS:
    def __init__(self, grafo: Navigator,heuristica=None):
        self.no_final = None
        self.grafo = grafo
        self.visitados = set()
    
    def _dfs(self, cur: int,try_plot=False) -> bool:
        
        self.visitados.add(cur)
        if try_plot:
            mostra_grafo(self.grafo)
        
        for outro in self.grafo.get_neighboors(cur):            
            if outro not in self.visitados:
                self.grafo.nav(cur, outro)
                
                print(f'DFS: Indo de {cur} -> {outro}')
                if outro == self.no_final or self._dfs(outro,try_plot=try_plot):
                    return True
                
        return False
        
        
    def run(self, no_inicial: int, no_final: int,try_plot=False) -> bool:
        if no_inicial == no_final:
            return True
        
        self.no_final = no_final
        self.visitados.clear()
        return self._dfs(no_inicial,try_plot=try_plot)


class BFS:
    def __init__(self, grafo: Navigator,heuristica=None):
        self.grafo = grafo  
    
    def run(self, no_inicial: int, no_final: int,try_plot=False) -> bool:
        if no_inicial == no_final:
            return True
        
        fila = Queue()
        fila.put(no_inicial)
        
        visitados = set([no_inicial])
        
        while not fila.empty():
            if try_plot:
                mostra_grafo(self.grafo)
            
            cur = fila.get()
            print(f'BFS: Expandindo {cur}')
            
            for outro in self.grafo.get_neighboors(cur):
                if outro not in visitados:
                    self.grafo.nav(cur, outro)
                    visitados.add(outro)
                    
                    print(f'BFS: Indo de {cur} -> {outro}')
                    
                    if outro == no_final:
                        return True
                    
                    fila.put(outro)
        if try_plot:
            mostra_grafo(self.grafo)
        return False


class AEstrela:
    def __init__(self, grafo: Navigator, heuristica):
        # Heuristica eh uma funcao que recebe um inteiro e retorna
        # algum valor numerico >= 0 (int ou float)
        self.grafo = grafo
        self.heuristica = heuristica 
        self.heuristic_historic = []
    
    def run(self, no_inicial: int, no_final: int,try_plot=False,w:float=1) -> bool:
        if no_inicial == no_final:
            return True

        goal_xy = self.grafo.get_pos_goal()
        print(f'{goal_xy = }')
        
        fila = PriorityQueue()
        fila.put(PrioritizedItem(0, (no_inicial, 0)))
        
        # Mantem a menor distancia encontrada ate agora
        distancias = {no_inicial: 0}

        while not fila.empty():
            
            item = fila.get()
            (cur, dist) = item.item

            # Se depois de por na fila encontrou-se um caminho melhor
            # ignora 
            if cur in distancias and distancias[cur] < dist:
                continue

            print(f'Expandindo {cur} ({dist = })')
            
            for outro in self.grafo.get_neighboors(cur):
                peso = 1
                dist_outro = dist + peso
                
                # Se essa eh a melhor distancia encontrada ate agora
                if outro not in distancias or dist_outro < distancias[outro]:
                    self.grafo.nav(cur, outro)
                    if try_plot:
                        mostra_grafo(self.grafo)
                    if outro == no_final:
                        return True

                    # Calcula a estimativa do proximo vertice
                    # Usado para decidir a prioridade na fila
                    outro_xy = self.grafo.get_pos(outro)
                    est = self.heuristica(outro_xy,goal_xy)*w
                    # print(f"{outro_xy} -> {goal_xy}: {est}")
                    est_outro = dist_outro + est
                    self.heuristic_historic.append(est) ## guarda no histórico
                    
                    distancias[outro] = dist_outro                    
                    fila.put(PrioritizedItem(est_outro, (outro, dist_outro)))

                    print(f'Indo de {cur} -> {outro} ({outro_xy = }, {est = }, tot = {est_outro})')
        
        return False
    

class Dijkstra:
    def __init__(self, grafo: Navigator,heuristica=None):
        self.grafo = grafo
        self.heuristic_historic = []
    def run(self, no_inicial: int, no_final: int,try_plot=False) -> bool:
        aest = AEstrela(self.grafo, lambda p1,p2: 0)
        conseguiu_chegar = aest.run(no_inicial, no_final,try_plot=try_plot)
        return conseguiu_chegar


class BestFirstSearch:
    def __init__(self, grafo: Navigator, heuristica):
        self.grafo = grafo
        self.heuristica = heuristica 
        self.heuristic_historic = []

    def run(self, no_inicial: int, no_final: int, try_plot=False) -> bool:
        if no_inicial == no_final:
            return True
        
        fila = PriorityQueue()
        est = self.heuristica(self.grafo.get_pos(no_inicial),self.grafo.goal_xy)

        fila.put(PrioritizedItem(est, no_inicial))
        visited = set([no_inicial])
        
        while not fila.empty():
            getted = fila.get()
            cur = getted.item
            
            self.heuristic_historic.append(getted.priority)
            if try_plot:
                mostra_grafo(self.grafo)
            if cur == no_final:
                return True
            
            for outro in self.grafo.get_neighboors(cur):
                if outro not in visited:
                    self.grafo.nav(cur, outro)
                    visited.add(outro)
                
                    outro_xy = self.grafo.get_pos(outro)
                    est = self.heuristica(outro_xy,self.grafo.goal_xy)
                    fila.put(PrioritizedItem(est, outro))
        
        
        return False


class HillClimb:
    # Tem varios, nao sei se ele quer o que vai no primeiro
    # vizinho bom que achar ou o que vai no melhor vizinho
    # Implementei o mais facil, que e no primeiro vizinho
    
    def __init__(self, grafo: Navigator, heuristica):
        # A heuristica e uma estimativa da distancia do no atual
        # ate o destino
        
        self.grafo = grafo
        self.heuristica = heuristica        
        self.heuristic_historic = []
    def run(self, no_inicial: int, no_final: int,try_plot=False) -> bool:
        if no_inicial == no_final:
            return True
        
        cur = no_inicial
        inicial_xy = self.grafo.get_pos(no_inicial)
        cur_est = self.heuristica(inicial_xy,self.grafo.goal_xy)
        
        while cur != no_final:
            print(f'HillClimb: expandindo {cur} ({cur_est = })')
            
            for outro in self.grafo.get_neighboors(cur):
                outro_xy = self.grafo.get_pos(outro)
                est = self.heuristica(outro_xy,self.grafo.goal_xy)
                
                print(f'HillClimb: tentando {outro = } ({est = })')
                if est < cur_est:
                    self.grafo.nav(cur, outro)
                    if try_plot:
                        mostra_grafo(self.grafo)
                    print(f'HillClimb: inde de {cur} -> {outro}')
                    cur = outro
                    cur_est = est
                    self.heuristic_historic.append(est)    
                    break
            else:
                # Nao achou nenhum vizinho melhor
                if try_plot:
                    mostra_grafo(self.grafo)
                return False

        return True
    
