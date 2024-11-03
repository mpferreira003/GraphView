from navigator import Navigator
from queue import Queue, PriorityQueue 
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)


class DFS:
    def __init__(self, grafo: Navigator):
        self.no_final = None
        self.grafo = grafo
        self.visitados = set()

    def _dfs(self, cur: int) -> bool:
        self.visitados.add(cur)

        for outro in self.grafo.get_neighboors(cur):            
            if outro not in self.visitados:
                self.grafo.nav(cur, outro)
                if outro == self.no_final or _dfs(outro):
                    return True

        return False
        
        
    def run(self, no_inicial: int, no_final: int) -> bool:
        if no_inicial == no_final:
            return True
        
        self.no_final = no_final
        self.visitados.clear()
        return _dfs(no_inicial)


class BFS:
    def __init__(self, grafo: Navigator):
        self.grafo = grafo  

    def run(self, no_inicial: int, no_final: int) -> bool:
        if no_inicial == no_final:
            return True
        
        fila = Queue()
        fila.put(no_inicial)
        
        visitados = set()

        while not fila.empty():
            cur = fila.get()
            visitados.add(cur)
            for outro in self.grafo.get_neighboors(cur):
                if outro not in visitados:
                    self.grafo.nav(cur, outro)
                    if outro == no_final:
                        return True
                    
                    fila.put(outro)

        return False


class AEstrela:
    def __init__(self, grafo: Navigator, heuristica):
        # Heuristica eh uma funcao que recebe um inteiro e retorna
        # algum valor numerico >= 0 (int ou float)
        self.grafo = grafo
        self.heuristica = heuristica 

    def run(self, no_inicial: int, no_final: int) -> bool:
        if no_inicial == no_final:
            return True
        
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
            
            for outro in self.grafo.get_neighboors(cur):
                peso = 1
                dist_outro = dist + peso

                # Se essa eh a melhor distancia encontrada ate agora
                if outro not in distancias or dist_outro < distancias[outro]:
                    self.grafo.nav(cur, outro)
                    if outro == no_final:
                        return True

                    # Calcula a estimativa do proximo vertice
                    # Usado para decidir a prioridade na fila
                    est_outro = dist_outro + self.heuristica(outro)
                    
                    distancias[outro] = dist_outro                    
                    fila.put(PrioritizedItem(est_outro, (outro, dist_outro)))

        return False
    

class Dijkstra:
    def __init__(self, grafo: Navigator):
        self.grafo = grafo

    def run(self, no_inicial: int, no_final: int) -> bool:
        aest = AEstrela(grafo, lambda x: 0)
        return aest.run(no_inicial, no_final)


class BestFirstSearch:
    def __init__(self, grafo: Navigator, heuristica):
        self.grafo = grafo
        self.heuristica = heuristica 

    def run(self, no_inicial: int, no_final: int) -> bool:
        pass    
    
    