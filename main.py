from generator import MundoPequeno
from pipeline import *

## ---- cria as conexões
n = 100
mp = MundoPequeno(n,seed=42)
mp.create_data(dim=2)
mp.create_connections(3,0.02) ## k=3, p=0.1
connections = mp.get_connections()


## ---- roda o algoritmo
exp_name, delay, historic = pipeline(connections,
                                     'AEstrela',
                                     'euclidian',
                                     1,
                                     13,
                                     gif_name='batata',
                                     try_plot=True,
                                    #  nodes_positions=mp.embeddings,
                                     kwargs_gif = {'delay_frame':200},
                                    #  kwargs_run = {'max_it':20} ## dá pra colocar o w do AEstrela também
                                     )

if historic:
    plot_historic(exp_name,delay,historic)
