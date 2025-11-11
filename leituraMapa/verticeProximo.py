import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image

def load_tree_from_file(input_file):
    mst = {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            try:
                split_pos = line.find(': [')
                if split_pos == -1:
                    continue
                
                vertice_str = line[:split_pos]
                lista_str = '[' + line[split_pos + 3:]
                
                if not lista_str.endswith(']'):
                    lista_str += ']'
                
                vertice = eval(vertice_str)
                conexoes = eval(lista_str)
                
                if conexoes:
                    mst[vertice] = conexoes
                
            except Exception as e:
                continue
    
    return mst

def distancia(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def vertice_mais_proximo(posicao, arvore):
    if not arvore:
        return None, float('inf')
    
    distancia_min = float('inf')
    vertice_proximo = None
    
    for vertice in arvore.keys():
        dist = distancia(posicao, vertice)
        if dist < distancia_min:
            distancia_min = dist
            vertice_proximo = vertice
    
    return vertice_proximo, distancia_min

def plotar_pontos_teste(imagem_base, posicoes_teste, arvore, output_file):
    img = Image.open(imagem_base)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(img, extent=[0, 1000, 0, 1000])
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    
    for pos in posicoes_teste:
        vertice, dist = vertice_mais_proximo(pos, arvore)
        
        ax.plot(pos[0], pos[1], 'bo', markersize=6, zorder=10,
                markeredgecolor='darkblue', markeredgewidth=1.5)
        
        ax.text(pos[0], pos[1] - 20,
                f'({pos[0]}, {pos[1]})',
                fontsize=8,
                ha='center',
                va='top',
                color='darkblue',
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3',
                         facecolor='lightblue',
                         edgecolor='blue',
                         alpha=0.8,
                         linewidth=1.5),
                zorder=10)
        
        if vertice:
            ax.plot([pos[0], vertice[0]], [pos[1], vertice[1]], 
                   'b--', linewidth=1.5, alpha=0.6, zorder=5)
            
            mid_x = (pos[0] + vertice[0]) / 2
            mid_y = (pos[1] + vertice[1]) / 2
            ax.text(mid_x, mid_y, f'{dist:.1f}',
                   fontsize=7,
                   ha='center',
                   bbox=dict(boxstyle='round,pad=0.2',
                            facecolor='white',
                            edgecolor='blue',
                            alpha=0.9),
                   zorder=10)
    
    ax.set_title('Vértices Mais Próximos', fontsize=14, fontweight='bold')
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

def salvar_resultados_txt(resultados, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Resultados - Vértices Mais Próximos\n")
        f.write("# Formato: Posição -> Vértice Mais Próximo -> Distância\n")
        f.write("=" * 60 + "\n\n")
        
        for pos, vertice, dist in resultados:
            f.write(f"Posição: ({pos[0]}, {pos[1]})\n")
            f.write(f"Vértice Mais Próximo: ({vertice[0]}, {vertice[1]})\n")
            f.write(f"Distância: {dist:.2f}\n")
            f.write("-" * 40 + "\n")

if __name__ == "__main__":
    MST_FILE = '../mapa/mst_tree.txt'
    MST_IMAGE = '../leituraMapa/mst_kruskal.png'
    OUTPUT_IMAGE = 'vertices_proximos_teste.png'
    OUTPUT_TXT = 'resultados_vertices_proximos.txt'
    
    arvore = load_tree_from_file(MST_FILE)
    
    if not arvore:
        exit(1)
    
    posicoes_teste = [
        (100, 100),
        (500, 500),
        (800, 800),
        (300, 700),
    ]
    
    resultados = []
    for pos in posicoes_teste:
        vertice, dist = vertice_mais_proximo(pos, arvore)
        resultados.append((pos, vertice, dist))
    
    plotar_pontos_teste(MST_IMAGE, posicoes_teste, arvore, OUTPUT_IMAGE)
    print(f"Imagem gerada: {OUTPUT_IMAGE}")
    
    salvar_resultados_txt(resultados, OUTPUT_TXT)
    print(f"Arquivo TXT gerado: {OUTPUT_TXT}")
