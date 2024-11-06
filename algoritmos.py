"""
Este módulo contém implementações de diversos algoritmos de busca em grafos, 
incluindo DFS (Busca em Profundidade), BFS (Busca em Largura), A* (A Estrela), 
Dijkstra, Best First Search e Hill Climbing. Cada algoritmo é responsável 
por encontrar o caminho entre um nó inicial e um nó final, usando diferentes 
estratégias de exploração de nós. O código também utiliza a classe 'Navigator' 
para manipulação do grafo e visualização dos estados durante a execução.
"""


from navigator import Navigator
from queue import Queue, PriorityQueue
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PrioritizedItem:
    # Definição da classe PrioritizedItem para ser usada em filas de prioridade.
    priority: int  # Prioridade do item.
    # Item armazenado, sem ser comparado na ordenação.
    item: Any = field(compare=False)


TIME_PER_IT = 0.1  # Tempo entre as iterações para exibição, em segundos.


def mostra_grafo(grafo: Navigator, last=False):
    # Função para adicionar uma imagem do estado atual do grafo ao gif, se a opção for habilitada.
    grafo.add_imgtogif()


class DFS:
    def __init__(self, grafo: Navigator, heuristica=None):
        self.no_final = None  # O nó objetivo (final).
        self.grafo = grafo  # O grafo sobre o qual a busca será realizada.
        self.visitados = set()  # Conjunto para armazenar nós visitados.

    def _dfs(self, cur: int, try_plot=False) -> bool:
        # Função recursiva para realizar a busca em profundidade.
        self.visitados.add(cur)  # Marca o nó atual como visitado.
        if try_plot:
            mostra_grafo(self.grafo)  # Plota o grafo se 'try_plot' for True.

        # Para cada vizinho do nó atual.
        for outro in self.grafo.get_neighboors(cur):
            if outro not in self.visitados:
                # Realiza a navegação para o vizinho.
                self.grafo.nav(cur, outro)
                print(f'DFS: Indo de {cur} -> {outro}')
                if outro == self.no_final or self._dfs(outro, try_plot=try_plot):
                    return True  # Se encontrou o destino, retorna True.

        return False  # Se não encontrou o destino, retorna False.

    def run(self, no_inicial: int, no_final: int, try_plot=False) -> bool:
        # Função principal para rodar a busca em profundidade.
        if no_inicial == no_final:
            return True  # Se o nó inicial é o final, não há busca a ser feita.

        self.no_final = no_final  # Define o nó objetivo.
        self.visitados.clear()  # Limpa o conjunto de visitados.
        return self._dfs(no_inicial, try_plot=try_plot)  # Inicia a busca.


class BFS:
    def __init__(self, grafo: Navigator, heuristica=None):
        self.grafo = grafo  # O grafo sobre o qual a busca será realizada.

    def run(self, no_inicial: int, no_final: int, try_plot=False) -> bool:
        # Função principal para rodar a busca em largura.
        if no_inicial == no_final:
            return True  # Se o nó inicial é o final, não há busca a ser feita.

        fila = Queue()  # Cria uma fila para a busca em largura.
        fila.put(no_inicial)  # Adiciona o nó inicial à fila.

        visitados = set([no_inicial])  # Conjunto de nós visitados.

        while not fila.empty():
            if try_plot:
                # Plota o grafo se 'try_plot' for True.
                mostra_grafo(self.grafo)

            cur = fila.get()  # Pega o próximo nó da fila.
            print(f'BFS: Expandindo {cur}')

            # Para cada vizinho do nó atual.
            for outro in self.grafo.get_neighboors(cur):
                if outro not in visitados:
                    # Realiza a navegação para o vizinho.
                    self.grafo.nav(cur, outro)
                    visitados.add(outro)  # Marca o vizinho como visitado.

                    print(f'BFS: Indo de {cur} -> {outro}')

                    if outro == no_final:
                        return True  # Se encontrou o destino, retorna True.

                    fila.put(outro)  # Adiciona o vizinho à fila.

        if try_plot:
            mostra_grafo(self.grafo)  # Plota o grafo ao final da execução.
        return False  # Se não encontrou o destino, retorna False.


class AEstrela:
    def __init__(self, grafo: Navigator, heuristica):
        # Heuristica eh uma funcao que recebe um inteiro e retorna
        # algum valor numerico >= 0 (int ou float)
        self.grafo = grafo  # O grafo sobre o qual a busca será realizada.
        # Função heurística que estimará a distância até o objetivo.
        self.heuristica = heuristica
        self.heuristic_historic = []  # Histórico das heurísticas calculadas.

    def run(self, no_inicial: int, no_final: int, try_plot=False, w: float = 1) -> bool:
        # Função principal para rodar a busca A*.
        if no_inicial == no_final:
            return True  # Se o nó inicial é o final, não há busca a ser feita.

        goal_xy = self.grafo.get_pos_goal()  # Obtém a posição do objetivo.
        print(f'{goal_xy = }')

        fila = PriorityQueue()  # Fila de prioridade para a busca A*.
        # Adiciona o nó inicial à fila.
        fila.put(PrioritizedItem(0, (no_inicial, 0)))

        # Mantem a menor distancia encontrada ate agora
        # Dicionário com as distâncias até os nós.
        distancias = {no_inicial: 0}

        while not fila.empty():
            # Pega o item com menor prioridade (menor custo).
            item = fila.get()
            est = item.priority  # Estimativa do custo (prioridade).
            (cur, dist) = item.item  # Nó atual e sua distância.

            # Se depois de por na fila encontrou-se um caminho melhor, ignora
            if cur in distancias and distancias[cur] < dist:
                continue

            print(f'Expandindo {cur} ({dist = })')
            self.heuristic_historic.append(est)

            # Para cada vizinho do nó atual.
            for (outro, peso) in self.grafo.get_neighboors(cur, return_weight=True):
                dist_outro = dist + peso  # Calcula a nova distância.

                # Se essa é a melhor distância encontrada até agora
                if outro not in distancias or dist_outro < distancias[outro]:
                    # Realiza a navegação para o vizinho.
                    self.grafo.nav(cur, outro)
                    if try_plot:
                        # Plota o grafo se 'try_plot' for True.
                        mostra_grafo(self.grafo)
                    if outro == no_final:
                        return True  # Se encontrou o destino, retorna True.

                    # Calcula a estimativa do próximo vértice
                    outro_xy = self.grafo.get_pos(outro)
                    # Estimativa considerando o peso.
                    est = self.heuristica(outro_xy, goal_xy)*w
                    # Total de distância + estimativa.
                    est_outro = dist_outro + est

                    # Atualiza a distância para o vizinho.
                    distancias[outro] = dist_outro
                    # Adiciona o vizinho à fila de prioridade.
                    fila.put(PrioritizedItem(est_outro, (outro, dist_outro)))

                    print(
                        f'Indo de {cur} -> {outro} ({outro_xy = }, {est = }, tot = {est_outro})')

        return False  # Se não encontrou o destino, retorna False.


class Dijkstra:
    def __init__(self, grafo: Navigator, heuristica=None):
        self.grafo = grafo  # O grafo sobre o qual a busca será realizada.
        self.heuristic_historic = []  # Histórico das heurísticas calculadas.

    def run(self, no_inicial: int, no_final: int, try_plot=False) -> bool:
        # Função principal para rodar o algoritmo de Dijkstra.
        # Usando A* com heurística zero (sem consideração de estimativa).
        aest = AEstrela(self.grafo, lambda p1, p2: 0)
        # Chama A* para rodar Dijkstra.
        conseguiu_chegar = aest.run(no_inicial, no_final, try_plot=try_plot)
        return conseguiu_chegar  # Retorna o resultado da execução.


class BestFirstSearch:
    def __init__(self, grafo: Navigator, heuristica):
        self.grafo = grafo  # O grafo sobre o qual a busca será realizada.
        # Função heurística que estimará a distância até o objetivo.
        self.heuristica = heuristica
        self.heuristic_historic = []  # Histórico das heurísticas calculadas.

    def run(self, no_inicial: int, no_final: int, try_plot=False) -> bool:
        # Função principal para rodar a Best First Search (Busca Primeiro o Melhor).
        if no_inicial == no_final:
            return True  # Se o nó inicial é o final, não há busca a ser feita.

        fila = PriorityQueue()  # Fila de prioridade para a busca.
        # Estimativa da distância inicial.
        est = self.heuristica(self.grafo.get_pos(
            no_inicial), self.grafo.goal_xy)

        # Adiciona o nó inicial à fila de prioridade.
        fila.put(PrioritizedItem(est, no_inicial))
        visited = set([no_inicial])  # Conjunto de nós visitados.

        while not fila.empty():
            # Pega o item com menor prioridade (menor estimativa).
            getted = fila.get()
            cur = getted.item  # Nó atual.

            self.heuristic_historic.append(getted.priority)

            if try_plot:
                # Plota o grafo se 'try_plot' for True.
                mostra_grafo(self.grafo)
            if cur == no_final:
                return True  # Se encontrou o destino, retorna True.

            # Para cada vizinho do nó atual.
            for outro in self.grafo.get_neighboors(cur):
                if outro not in visited:
                    # Realiza a navegação para o vizinho.
                    self.grafo.nav(cur, outro)
                    visited.add(outro)  # Marca o vizinho como visitado.

                    # Obtém a posição do vizinho.
                    outro_xy = self.grafo.get_pos(outro)
                    # Estimativa de distância até o objetivo.
                    est = self.heuristica(outro_xy, self.grafo.goal_xy)
                    # Adiciona o vizinho à fila de prioridade.
                    fila.put(PrioritizedItem(est, outro))

        return False  # Se não encontrou o destino, retorna False.


class HillClimb:
    # Tem varios, nao sei se ele quer o que vai no primeiro
    # vizinho bom que achar ou o que vai no melhor vizinho
    # Implementei o mais facil, que e no primeiro vizinho

    def __init__(self, grafo: Navigator, heuristica):
        # A heuristica e uma estimativa da distancia do no atual
        # ate o destino
        self.grafo = grafo  # O grafo sobre o qual a busca será realizada.
        # Função heurística que estimará a distância até o objetivo.
        self.heuristica = heuristica
        self.heuristic_historic = []  # Histórico das heurísticas calculadas.

    def run(self, no_inicial: int, no_final: int, try_plot=False) -> bool:
        # Função principal para rodar a Hill Climb (Escalada de Colina).
        if no_inicial == no_final:
            return True  # Se o nó inicial é o final, não há busca a ser feita.

        cur = no_inicial  # Começa no nó inicial.
        inicial_xy = self.grafo.get_pos(no_inicial)  # Posição do nó inicial.
        # Estimativa inicial.
        cur_est = self.heuristica(inicial_xy, self.grafo.goal_xy)

        while cur != no_final:
            print(f'HillClimb: expandindo {cur} ({cur_est = })')

            # Para cada vizinho do nó atual.
            for outro in self.grafo.get_neighboors(cur):
                # Obtém a posição do vizinho.
                outro_xy = self.grafo.get_pos(outro)
                # Estimativa de distância até o objetivo.
                est = self.heuristica(outro_xy, self.grafo.goal_xy)

                print(f'HillClimb: tentando {outro = } ({est = })')
                if est < cur_est:  # Se encontrou um vizinho melhor.
                    self.grafo.nav(cur, outro)  # Realiza a navegação.
                    if try_plot:
                        # Plota o grafo se 'try_plot' for True.
                        mostra_grafo(self.grafo)
                    print(f'HillClimb: inde de {cur} -> {outro}')
                    cur = outro  # Move para o próximo nó.
                    cur_est = est  # Atualiza a estimativa.
                    self.heuristic_historic.append(est)
                    break
            else:
                # Nao achou nenhum vizinho melhor
                if try_plot:
                    # Plota o grafo ao final da execução.
                    mostra_grafo(self.grafo)
                # Se não encontrou um vizinho melhor, retorna False.
                return False

        return True  # Se chegou ao objetivo, retorna True.
