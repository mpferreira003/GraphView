## Como usar os bagui:

Pra rodar o algoritmo, você vai precisar usar o Navegador (navigator.py).

### Etapas:
    1 - Forneça nó a nó as conexões e as distâncias por meio do método Navigator.add
        (leia a função específica, lá está documentado como realizar esse processo)
    2 - depois de passar todos os nós da rede, chame o método '.compile()' para 
    criar os objetos Node. Nesta função é possível passar parâmetros 
    para o plot da rede (cor dos nós, tamanho etc), porém é recomendável realizar 
    novamente esta etapa através do '.set_attributes(...)', já que o processo do 
    compile é custoso e aí você pode simplesmente testar várias combinações dos 
    atributos de plot de maneira mais fácil.
    3 - depois de chamar o '.compile()', você já pode setar quais nós já foram navegados 
    ou não através do método 'nav(destino,aresta)'. Ao ativar este método, ele pinta a 
    conexão (aresta) e a nó de destino. Note que caso o nó de destino já tenha sido alcançado 
    previamente, somente a aresta será pintada.