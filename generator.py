import numpy as np
from math import sqrt
import pickle
from typing import cast

"""
Pacote responsável por gerar a rede de pequeno mundo
"""


def cosine_f(u, v): return np.sum(u*v) / \
    (sqrt(np.sum(u**2)) * sqrt(np.sum(v**2)))


def euclidian_f(u, v): return sqrt(np.sum((u-v)**2))


metrics = {
    'euclidean': euclidian_f,
    'cosine': cosine_f
}


class MundoPequeno():
    def __init__(self, n: int, seed=None):
        """
        Args:
            n:int - quantidade de nós
            seed:int - seta a seed do numpy para a geração dos dados
        """
        self.n = n
        self.has_connections = False
        self.has_data = False

        # etapa de colocar a seed de geração
        self.set_seed(seed)

    def set_seed(self, seed):
        if seed is None:
            self.seed = np.random.randint(0, np.iinfo(np.int32).max)
        else:
            self.seed = seed
        print(f"Seed: {self.seed}")
        np.random.seed(self.seed)

    def create_data(self, dim: int = 2, space: int = 1, metric: str = 'euclidean', verbose=False):
        """
        Cria embeddings Ndimensionais e a matriz de distâncias
        Args:
            dim:int [default=2] - dimensão das embeddings
            space:int [default=1] - espaço das embeddings. Aumentar
                isso torna o espaço mais esparso.
        """
        self.space = space
        self.metric = metric
        metric_f = metrics[metric]
        self.embeddings = np.random.rand(self.n, dim)*space
        self.has_data = True

        # if verbose: print("embeddings:\n",self.embeddings,'\n\n')
        # Cria a matriz de distâncias
        self.distances = np.array([[0,]*self.n] * self.n, dtype=np.float64)
        for i in range(self.n):
            for j in range(i+1, self.n):  # a matriz é espelhada, então só calcula uma parte
                u = self.embeddings[i]
                v = self.embeddings[j]
                self.distances[i][j] = metric_f(u, v)
                self.distances[j][i] = self.distances[i][j]
            if verbose:
                print(f"Calculating distances: {100 * float(i) / self.n:.2f}%")

        # if verbose: print("Distances:\n",self.distances,'\n\n')

        # Organiza pelos vizinhos mais próximos
        self.organized_nearest = np.argsort(self.distances, axis=1)
        # dropa o primeira conexão (ele mesmo), ficando uma matriz NxN-1
        self.organized_nearest = self.organized_nearest[:, 1:]
        # if verbose: print("organized_nearest:\n",self.organized_nearest,'\n\n')

    def create_connections(self, k: int, p: int, verbose=False):
        """
        Função para gerar as conexões 
        Args:
            k:int - quantidade de conexões mais próximas de cada nó
            p:int - fração dos nós que possuem conexão com nós distantes
        """
        if not self.has_data:
            raise ValueError(
                "Erro - você deve chamar o .create_data para gerar os dados e as distâncias")

        self.k = k
        self.p = p
        self.has_connections = True

        # seleciona as K primeiras colunas para fazer diretamente as conexões
        k_neighboors_links = self.organized_nearest[:, :self.k].astype(int)
        if verbose:
            print('k_neighboors_links: \n', k_neighboors_links, '\n\n')

        self.connections = []  # lista que recebe a tupla (i,j,distancia)
        for i in range(self.n):
            package = np.transpose([np.full(
                (self.k,), i), k_neighboors_links[i], self.distances[i, k_neighboors_links[i]]])
            self.connections.extend(package.tolist())
            self.connections.extend(package[:, [1, 0, 2]].tolist())
        if verbose:
            print('connections: \n', np.array(self.connections), '\n\n')

        # conexão com nós distantes:
           # seleciona p nós aleatórios para se conectarem a nós distantes
        p_quantity = int(self.n * p)
        p_choosed_nodes = np.random.choice(self.n, size=(p_quantity,))
        if verbose:
            print(
                f' os nós p_choosed_nodes[{p_quantity}] terão conexão com um nó distante: {p_choosed_nodes}')

           # sorteia a posição de cada um, considerando que deve ser entre k e n-1
        random_sorted = np.random.randint(self.k, self.n-1, size=(p_quantity,))

        far_neighboors = self.organized_nearest[p_choosed_nodes, random_sorted]
        if verbose:
            print(f'far_neighboor: {far_neighboors}')

        for node, neighboor in list(zip(p_choosed_nodes, far_neighboors)):
            distance = self.distances[node][neighboor]
            self.connections.append(
                [int(neighboor), int(node), float(distance)])
            self.connections.append(
                [int(node), int(neighboor), float(distance)])

    def get_connections(self):
        if not self.has_connections:
            raise ValueError("""Erro - o seu grafo de mundo pequeno não possui conexões. 
                             Verifique se você rodou a função .create_data e .create_connections""")
        return self.connections

    def save(self):
        """
        Função que permite salvar o grafo de pequeno mundo gerado
        em um arquivo .pkl
        """
        graph_name = f'{self.n}nodes'
        if self.has_connections:
            graph_name += f'_k={self.k}_p={self.p}'
        else:
            graph_name += '_NoConnections'

        with open(f"{graph_name}.pkl", "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load(file_name: str):
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
            return cast(MundoPequeno, file)


if __name__ == "__main__":
    n = 10
    mp = MundoPequeno(n, seed=42)
    mp.create_data(dim=2)
    mp.create_connections(3, 0.1, verbose=True)
    connections = mp.get_connections()
