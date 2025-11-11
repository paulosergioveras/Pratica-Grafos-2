import math

def load_tree_from_file(input_file):
    mst = {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                vertice_str, conexoes_str = line.split(': [')
                conexoes_str = conexoes_str.rstrip(']')
                vertice = eval(vertice_str)
                
                conexoes = []
                if conexoes_str:
                    partes = conexoes_str.split('), (')
                    for parte in partes:
                        parte = parte.strip('()').strip()
                        if parte:
                            coords_peso = parte.split(', ')
                            if len(coords_peso) >= 3:
                                x = float(coords_peso[0])
                                y = float(coords_peso[1])
                                peso = float(coords_peso[2])
                                conexoes.append(((x, y), peso))
                
                mst[vertice] = conexoes
                
            except Exception as e:
                continue
    
    return mst

def distancia(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def vertice_mais_proximo(posicao, arvore):
    distancia_min = float('inf')
    vertice_proximo = None
    
    for vertice in arvore.keys():
        dist = distancia(posicao, vertice)
        
        if dist < distancia_min:
            distancia_min = dist
            vertice_proximo = vertice
    
    return vertice_proximo, distancia_min

if __name__ == "__main__":
    MST_FILE = '../mapa/mst_tree.txt'
    print("Carregando árvore...")
    arvore = load_tree_from_file(MST_FILE)
    print(f"Árvore carregada: {len(arvore)} vértices\n")
    
    # Testar com várias posições
    posicoes_teste = [
        (100, 100),   # Perto do obstáculo 1
        (500, 500),   # Centro do mapa
        (700, 700),   # Perto do obstáculo 4
        (250, 200),   # Posição aleatória
    ]
    
    print("=" * 60)
    print("TESTE: Encontrando vértices mais próximos")
    print("=" * 60)
    
    for pos in posicoes_teste:
        vertice, dist = vertice_mais_proximo(pos, arvore)
        print(f"\nPosição: {pos}")
        print(f"Vértice mais próximo: {vertice}")
        print(f"Distância: {dist:.2f} unidades")
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
