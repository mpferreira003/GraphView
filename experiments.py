from generator import MundoPequeno
from pipeline import *
import os
import time
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

def create_rede(n,k,p):
    mp = MundoPequeno(n, seed=42)
    mp.create_data(dim=2)
    mp.create_connections(k, p)
    return mp

n=200
k=7
quantity_tests=15
algorithms_to_run = list(algorithms.keys())



testes = (
    {'n':n,'k':k,'p':10/100},
    # {'n':n,'k':k,'p':5/100},
    # {'n':n,'k':k,'p':1/100},
)
print("Instanciando experimentos ----")
    

main_path = os.path.dirname(os.path.abspath(__file__))    
redes=[]
for teste in testes:
    n,k,p = teste.values()
    file_path = f'saves/{n}nodes_k={k}_p={p}.pkl'
    print(' '*2,f"Verificando existência de backup [{file_path}]...")
    
    file_path = os.path.join(main_path, file_path)
    if not os.path.isfile(file_path):
        print(' '*4,'Arquivo não encontrado. Realizando criação de rede Mundo Pequeno') 
        rede = create_rede(n,k,p)
        rede.save(relative_path='saves')
        print(' '*4,'Rede criada e salva com sucesso')
    else:
        rede = MundoPequeno.load(file_path)
        print(' '*4,"Arquivo encontrado. Rede obtida por backup")
    redes.append((rede,(n,k,p)))







## Configurando experimentos
AEstrela_w = 10
def run_pipeline(algorithm_name:str,
                 rede:MundoPequeno,
                 initial:int,
                 goal:int,
                 heuristica='euclidian'
                 ):
    if algorithm_name=='AEstrela':
        kwargs_run = {'w':AEstrela_w}
    elif algorithm_name=='BestFirst':
        kwargs_run = {}#{'max_it':BestFirstSearch_maxit}
    else:
        kwargs_run = {}
    
    results = pipeline(
        rede.get_connections(),        # Conexões geradas no mundo pequeno
        algorithm_name,                # Nome do algoritmo
        heuristica,                    # Nome da heurística: Euclidiana
        initial,                       # Nó inicial para a busca (nó 1)
        goal,                          # Nó objetivo para a busca (nó 13)
        nodes_positions=rede.embeddings,
        kwargs_run = kwargs_run
    )
    return results


def run_test(algorithm_name:str,
             rede:MundoPequeno,
             quantity_tests=10,
             heuristica='euclidian'):
    
    
    delay_mean = 0
    dist_mean = 0
    steps_mean = 0
    multi_historic = []
    chegou_stats = []
    for i in range(quantity_tests):
        initial = random.randint(0,n-1)
        goal = random.randint(0,n-1)
        exp_name,delay,dist,chegou,steps,historic = run_pipeline(algorithm_name,rede,initial,goal,heuristica=heuristica)
        delay_mean+=delay
        dist_mean+=dist
        steps_mean+=steps
        multi_historic.append(historic)
        chegou_stats.append(chegou)
    delay_mean/=quantity_tests
    dist_mean/=quantity_tests
    steps_mean/=quantity_tests
    if all(chegou_stats):
        chegou_stats=2 ## todos chegaram
    elif any(chegou_stats):
        chegou_stats=1 ## algum chegou
    else:
        chegou_stats=0 ## nenhum chegou
        
    
    return exp_name,delay_mean,dist_mean,chegou_stats,steps_mean,multi_historic





########## Etapa de análise dos resultados


estatisticas = []
for (rede,(n,k,p)) in redes:
    print("\n"*4,f'==================== Rodando experimento n={n} k={k} p={p}')
    
    algorithms_results=[]
    for algorithm_name in algorithms_to_run:
        print(' '*2,f'Rodando algoritmo [{algorithm_name}] em 3s...')
        # time.sleep(3)
        results = run_test(algorithm_name,rede,quantity_tests=quantity_tests)
        algorithms_results.append(results)
        print('\n\n')
    estatisticas.append(((n,k,p),algorithms_to_run,algorithms_results))



def set_bars_values(bars,Y):
    for barra, valor in zip(bars, Y):
            ax.text(
                barra.get_x() + barra.get_width() / 2,  # posição X
                barra.get_height(),  # posição Y
                valor,  # texto (valor de Y)
                ha='center',  # alinhamento horizontal
                va='bottom',  # alinhamento vertical
                fontsize=6
            )

colors = np.random.randint(100,200,size=(quantity_tests,3),dtype=int)
colors = [(float(a[0]/255),float(a[1]/255),float(a[2]/255)) for a in colors]
for (n,k,p),algorithms_name,algorithms_results in estatisticas:
    fig,axs = plt.subplots(2,3,figsize=(3*6,2*4))
    fig.suptitle(f"Rede mundo pequeno n={n} k={k} p={p}")
    exp_names,delay_times,dist_percs,chegou_stats,steps,heur_hists = [[r[i] for r in algorithms_results] for i in range(6)]
    
    cores = ['g' if stats==2 else ('y' if stats==1 else 'r') for stats in chegou_stats]
    patch_chegou = mpatches.Patch(color='g', label='todos')
    patch_depende = mpatches.Patch(color='y', label='alguns')
    patch_nao = mpatches.Patch(color='r', label='nenhum')
    
    
    ## Plot de comparação de distâncias
    ax=axs[0][0]
    ax.set_title("Comparação de distâncias")
    ax.set_ylabel("Distância média percorrida")
    bars = ax.bar(algorithms_name,dist_percs,color=cores)
    print("Steps: ",steps)
    print("dist_percs: ",dist_percs)
    set_bars_values(bars,[f'{d:.2f} \\{s:.1f}' for d,s in list(zip(dist_percs,steps))])
    ax.get_yaxis().set_visible(False)
    ax.legend(handles=[patch_chegou,patch_depende,patch_nao])
    ax.tick_params(axis='x',rotation=60)
    
    ## Plot de comparação de tempo
    delay_times = np.array(delay_times)*1000
    ax=axs[1][0]
    ax.set_title("Comparação de tempo (ms)")
    ax.set_ylabel("Tempo médio")
    bars = ax.bar(algorithms_name,delay_times,color=cores)
    set_bars_values(bars,[f'{d:.2f} \\{s:.1f}' for d,s in list(zip(delay_times,steps))])
    ax.get_yaxis().set_visible(False)
    ax.legend(handles=[patch_chegou,patch_depende,patch_nao])
    ax.tick_params(axis='x',rotation=60)
    
    ## Plots de comparação de heurística
    heuristic_indexes = [2,4,5]
    algorithms_name_c = [algorithms_name[i] for i in heuristic_indexes]
    heur_hists_c = [heur_hists[i] for i in heuristic_indexes]
    for i,(algorithm_name,algorithm_hists) in enumerate(list(zip(algorithms_name_c,heur_hists_c))):
        ax = axs[i%2][1+int((i+0.5)/2)]
        ax.set_title(f"Heurística {algorithm_name}")
        max_len = max([len(hist) for hist in algorithm_hists])
        for j,hist in enumerate(algorithm_hists):
            if len(hist)==0:
                continue
            # print("colors[j]: ",colors[j])
            plot_historic(heuristic_historic=hist,ax=ax,plt_color=colors[j])
    
        # Calcula o intervalo do eixo y com base no valor máximo da heurística e seu desvio padrão
        y_max_range = np.max([np.max(h) for h in algorithm_hists if len(h)>0]) + np.max([np.std(h) for h in algorithm_hists if len(h)>0])
        plt.ylim(0, y_max_range)
    
    plt.tight_layout()
    # plt.subplots_adjust(hspace=0.5)
    plt.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.1)
    plt.show()