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


TIME_PER_IT = 0.25
#TIME_PER_IT = 0

def mostra_grafo(grafo: Navigator, last=False):
    img = grafo.plot()
    cv2.imshow('Grafo',img)
    if not last:
        cv2.waitKey(20)
        time.sleep(TIME_PER_IT)


class DFS:
    def __init__(self, grafo: Navigator):
        self.no_final = None
        self.grafo = grafo
        self.visitados = set()

    def _dfs(self, cur: int) -> bool:
        mostra_grafo(self.grafo)
        self.visitados.add(cur)

        for outro in self.grafo.get_neighboors(cur):            
            if outro not in self.visitados:
                self.grafo.nav(cur, outro)
                print(f'DFS: Indo de {cur} -> {outro}')
                if outro == self.no_final or self._dfs(outro):
                    return True

        return False
        
        
    def run(self, no_inicial: int, no_final: int) -> bool:
        if no_inicial == no_final:
            return True
        
        self.no_final = no_final
        self.visitados.clear()
        return self._dfs(no_inicial)


class BFS:
    def __init__(self, grafo: Navigator):
        self.grafo = grafo  

    def run(self, no_inicial: int, no_final: int) -> bool:
        if no_inicial == no_final:
            return True
        
        fila = Queue()
        fila.put(no_inicial)
        
        visitados = set([no_inicial])

        while not fila.empty():
            mostra_grafo(self.grafo)
            
            cur = fila.get()
            print(f'BFS: Expandindo {cur}')

            for outro in self.grafo.get_neighboors(cur):
                if outro not in visitados:
                    self.grafo.nav(cur, outro)
                    visitados.add(cur)

                    print(f'BFS: Indo de {cur} -> {outro}')
                    
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
            mostra_grafo(self.grafo)
            
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

    def run(self, no_inicial: int, no_final: int, max_it: int = 100) -> bool:
        if no_inicial == no_final:
            return True
        
        fila = PriorityQueue()
        fila.put(PrioritizedItem(0, no_inicial))

        while not fila.empty() and max_it > 0:
            mostra_grafo(self.grafo)
                    
            max_it -= 1
            cur = fila.get().item

            if cur == no_final:
                return True
            
            ultimo = cur
            
            for outro in self.grafo.get_neighboors(cur):
                self.grafo.nav(cur, outro)
                
                est = self.heuristica(outro)
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

    def run(self, no_inicial: int, no_final: int) -> bool:
        if no_inicial == no_final:
            return True

        cur = no_inicial
        cur_est = self.heuristica(no_inicial)

        while cur != no_final:
            mostra_grafo(self.grafo)
            print(f'HillClimb: expandindo {cur} ({cur_est = })')
            
            for outro in self.grafo.get_neighboors(cur):
                est = self.heuristica(outro)
                print(f'HillClimb: tentando {outro = } ({est = })')
                if est < cur_est:
                    self.grafo.nav(cur, outro)
                    print(f'HillClimb: inde de {cur} -> {outro}')
                    cur = outro
                    cur_est = est

                    break
            else:
                # Nao achou nenhum vizinho melhor
                return False

        return True
    
