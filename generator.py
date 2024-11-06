import numpy as np
from math import sqrt
import pickle
from typing import cast

"""
Este código é responsável por gerar um grafo de pequeno mundo, no qual a maioria dos nós
está conectada a nós próximos, mas alguns nós têm conexões com nós distantes.
A rede gerada possui propriedades típicas de redes complexas, como alta conectividade e 
caminhos curtos entre os nós.
O processo envolve duas etapas principais: geração de dados (embeddings e distâncias) 
e geração de conexões entre os nós.
"""

# Função para calcular a similaridade cosseno entre dois vetores u e v


def cosine_f(u, v):
    return np.sum(u * v) / (sqrt(np.sum(u ** 2)) * sqrt(np.sum(v ** 2)))

# Função para calcular a distância euclidiana entre dois vetores u e v


def euclidian_f(u, v):
    return sqrt(np.sum((u - v) ** 2))


# Dicionário de métricas disponíveis para o cálculo de distâncias
metrics = {
    'euclidean': euclidian_f,  # Distância Euclidiana
    'cosine': cosine_f         # Similaridade Cosseno
}


class MundoPequeno():
    def __init__(self, n: int, seed=None):
        """
        Inicializa o grafo de Mundo Pequeno.
        Args:
            n: int - número de nós no grafo
            seed: int - semente para a geração aleatória dos dados
        """
        self.n = n
        self.has_connections = False  # Indicador se as conexões foram geradas
        # Indicador se os dados (embeddings e distâncias) foram gerados
        self.has_data = False

        # Define a semente para a geração aleatória
        self.set_seed(seed)

    def set_seed(self, seed):
        """
        Define a semente para geração aleatória de números.
        Args:
            seed: int - semente para a geração dos dados aleatórios
        """
        if seed is None:
            self.seed = np.random.randint(0, np.iinfo(np.int32).max)
        else:
            self.seed = seed
        print(f"Seed: {self.seed}")
        np.random.seed(self.seed)

    def create_data(self, dim: int = 2, space: int = 1, metric: str = 'euclidean', verbose=False):
        """
        Gera os dados de embeddings dos nós e a matriz de distâncias entre os nós.
        Args:
            dim: int [default=2] - dimensão das embeddings dos nós
            space: int [default=1] - fator de espaçamento entre os nós (aumenta o espaço entre eles)
            metric: str [default='euclidean'] - métrica usada para calcular a distância ('euclidean' ou 'cosine')
            verbose: bool [default=False] - se True, exibe informações durante a execução
        """
        self.space = space
        self.metric = metric
        # Seleção da função de distância de acordo com a métrica
        metric_f = metrics[metric]

        # Gera embeddings aleatórias para os nós no espaço definido
        self.embeddings = np.random.rand(self.n, dim) * space
        self.has_data = True  # Marca que os dados foram gerados

        # Criação da matriz de distâncias entre os nós
        self.distances = np.array([[0, ] * self.n] * self.n, dtype=np.float64)
        for i in range(self.n):
            for j in range(i + 1, self.n):  # A matriz é simétrica, então só calcula uma metade
                u = self.embeddings[i]
                v = self.embeddings[j]
                self.distances[i][j] = metric_f(u, v)
                self.distances[j][i] = self.distances[i][j]
            if verbose:
                print(f"Calculating distances: {100 * float(i) / self.n:.2f}%")

        # Organiza os nós pelos vizinhos mais próximos
        self.organized_nearest = np.argsort(self.distances, axis=1)
        # Remove o próprio nó de cada linha (auto-conexão)
        self.organized_nearest = self.organized_nearest[:, 1:]
        if verbose:
            print("organized_nearest:\n", self.organized_nearest, '\n\n')

    def create_connections(self, k: int, p: int, verbose=False):
        """
        Gera as conexões do grafo de pequeno mundo.
        Args:
            k: int - número de conexões mais próximas de cada nó
            p: int - fração de nós que terão conexões com nós distantes
            verbose: bool [default=False] - se True, exibe informações durante a execução
        """
        # Verifica se os dados já foram gerados antes de criar as conexões
        if not self.has_data:
            raise ValueError(
                "Erro - você deve chamar o .create_data para gerar os dados e as distâncias")

        self.k = k
        self.p = p
        self.has_connections = True  # Marca que as conexões foram geradas

        # Seleciona as k conexões mais próximas para cada nó
        k_neighboors_links = self.organized_nearest[:, :self.k].astype(int)
        if verbose:
            print('k_neighboors_links: \n', k_neighboors_links, '\n\n')

        # Lista para armazenar as conexões (i, j, distância)
        self.connections = []
        for i in range(self.n):
            package = np.transpose([np.full(
                (self.k,), i), k_neighboors_links[i], self.distances[i, k_neighboors_links[i]]])
            self.connections.extend(package.tolist())
            # Adiciona as conexões inversas (de i para j e de j para i)
            self.connections.extend(package[:, [1, 0, 2]].tolist())
        if verbose:
            print('connections: \n', np.array(self.connections), '\n\n')

        # Conexões com nós distantes:
        # Número de nós que terão conexões distantes
        p_quantity = int(self.n * p)
        p_choosed_nodes = np.random.choice(self.n, size=(p_quantity,))
        if verbose:
            print(
                f' os nós p_choosed_nodes[{p_quantity}] terão conexão com um nó distante: {p_choosed_nodes}')

        # Sorteia os nós distantes com base na distância
        random_sorted = np.random.randint(
            self.k, self.n - 1, size=(p_quantity,))

        far_neighboors = self.organized_nearest[p_choosed_nodes, random_sorted]
        if verbose:
            print(f'far_neighboor: {far_neighboors}')

        # Adiciona as conexões distantes
        for node, neighboor in list(zip(p_choosed_nodes, far_neighboors)):
            distance = self.distances[node][neighboor]
            self.connections.append(
                [int(neighboor), int(node), float(distance)])
            self.connections.append(
                [int(node), int(neighboor), float(distance)])

    def get_connections(self):
        """
        Retorna as conexões geradas.
        Lança um erro se as conexões não foram geradas.
        """
        if not self.has_connections:
            raise ValueError("""Erro - o seu grafo de mundo pequeno não possui conexões. 
                             Verifique se você rodou a função .create_data e .create_connections""")
        return self.connections

    def save(self):
        """
        Salva o grafo de pequeno mundo gerado em um arquivo .pkl
        """
        graph_name = f'{self.n}nodes'
        if self.has_connections:
            graph_name += f'_k={self.k}_p={self.p}'
        else:
            graph_name += '_NoConnections'

        # Salva o grafo em um arquivo binário .pkl
        with open(f"{graph_name}.pkl", "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load(file_name: str):
        """
        Carrega um grafo de pequeno mundo a partir de um arquivo .pkl.
        Args:
            file_name: str - nome do arquivo do grafo
        Returns:
            MundoPequeno - o grafo carregado do arquivo
        """
        file_name += '.pkl' if '.pkl' not in file_name else ''
        with open(file_name, "rb") as file:
            file = pickle.load(file)
            return cast(MundoPequeno, file)


# Teste do código (executado se for o script principal)
if __name__ == "__main__":
    n = 10  # Número de nós no grafo
    mp = MundoPequeno(n, seed=42)  # Cria o grafo com 10 nós e semente 42
    mp.create_data(dim=2)  # Cria os dados (embeddings) em 2D
    # Cria as conexões com k=3 e p=0.1
    mp.create_connections(3, 0.1, verbose=True)
    connections = mp.get_connections()  # Obtém as conexões geradas
