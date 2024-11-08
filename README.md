# Tutorial
Primeramente, bom dia, este arquivo serve como guia sobre como funciona o nosso trabalho.

## Como instalar?
Para instalar, sugiro que você crie um ambiente python. Se você estiver usando Linux, faça:
*Considero que você está dentro da pasta "GraphView", logo depois de clonar do github*
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

com isso você estará pronto para prosseguir no tutorial.

## Atuando sobre as redes
- **Criando a rede**: Para criar a rede em si, é utilizada a classe **MundoPequeno** disponível em **generator.py**. Nesta classe ocorre tanto a geração de embeddings aleatórias, bem como são calculadas as distâncias entre elas para fazer a primeira etapa, a **KNN**, e depois, em seguida, sorteia-se aleatóriamente uma proporção **p** de conexões distantes (tratamos 'distantes' como 'não sendo as k primeiras'). 
- **Atuando sobre as redes**: Preferimos separar a geração de rede das classes responsáveis por fazer plots e cálculos em cima dela. Existe a classe **VisualGraph**, disponível em **grafo.py**, que é estendida para a classe **Navigator** de **navigator.py**. O código em alto nível, só trabalha com o Navigator, que possibilita ao sistema os seguintes recursos:
    - Possui um sistema interno de mapeamento
    - Gravar quais nós o algoritmo passou (são pintados em vermelho por padrão)
    - Calcula a quantidade de *steps* e distância acumulada
    - Faz um gif com as etapas do algoritmo

## Algoritmos
Os algoritmos podem ser encontrados em **algoritmos.py**. Para cada um deles que é requerido no trabalho, existe uma classe específica destinada a ele. Essas classes possuem ligação com o objeto **Navigator** explicado anteriormente, sendo capaz de fornecer quais são os **vizinhos** de cada nó e retornar a **posição** deles, que é usada na heurística (confira o *heuristicas.py*).

## Como rodar?
Primeiramente, para criar exemplos, sugiro que rode o *main.py*. Por padrão ele fará uma rede bem simples e usará o algoritmo **BestFirstSearch** nela. Ao fim do algoritmo, ele mostrará um plot de como foi a heurística calculada durante cada step do algoritmo até chegar no objetivo. Perceba também que ele 
criará um GIF dentro da pasta *saves*, que mostra o passo a passo que o algoritmo tomou.

Depois, você pode rodar a *experiments.py*, que também irá utilizar o pipeline de *pipeline.py* para rodar todos os algoritmos, com vários grafos, várias vezes (com goals e posições iniciais variando). Ao fim, serão mostrados os gráficos de comparação de tempo e de distância percorrida e também os gráficos mostrando o desenvolvimento das heurísticas dos algoritmos que a utilizam.

## Observações
1 - Como não havia um padrão, fazer a contagem de quando acabou uma *step* de um algoritmo, dependeu somente de nossa própria implementação, ou seja, alguns algoritmos podem estar com uma alta contagem de steps simplesmente por que eles são contabilizados de forma diferente na sua programação interna.
2 - O grafo é gerado entre 0 e 1 e é multiplicado por um fator 'space', que é passado nos experimentos como sendo igual a 'n', como descrito no trabalho