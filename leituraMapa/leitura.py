import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math

def read_map(file):
    obstacles = []
    with open(file, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        if lines[i].strip() == 'OBSTACLE':
            i += 1
            num_vertices = int(lines[i].strip())
            i += 1
            vertices = [(float(lines[i+j].split(',')[0]), float(lines[i+j].split(',')[1])) 
                       for j in range(num_vertices)]
            obstacles.append(vertices)
            i += num_vertices
        else:
            i += 1
    
    return obstacles

def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

def segments_intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    j = len(polygon) - 1
    
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside

def is_visible(p1, p2, obstacles):
    # Verifica interseção com arestas
    for obstacle in obstacles:
        for i in range(len(obstacle)):
            edge_start = obstacle[i]
            edge_end = obstacle[(i + 1) % len(obstacle)]
            
            if (p1 in [edge_start, edge_end] or p2 in [edge_start, edge_end]):
                continue
            
            if segments_intersect(p1, p2, edge_start, edge_end):
                return False
    
    mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    return not any(point_in_polygon(mid, obs) for obs in obstacles)

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def create_visibility_graph(map_file):
    obstacles = read_map(map_file)
    vertices = list(set(v for obs in obstacles for v in obs))
    
    graph = {v: [] for v in vertices}
    
    for i, v1 in enumerate(vertices):
        for v2 in vertices[i+1:]:
            if is_visible(v1, v2, obstacles):
                dist = distance(v1, v2)
                graph[v1].append((v2, dist))
                graph[v2].append((v1, dist))
    
    return graph, vertices

def kruskal_mst(graph, vertices):
    edges = sorted(set((distance(v1, v2), tuple(sorted([v1, v2]))) 
                      for v1 in graph for v2, _ in graph[v1]))
    edges = [(w, e[0], e[1]) for w, e in edges]
   
    parent = {v: v for v in vertices}
    
    def find(v):
        if parent[v] != v:
            parent[v] = find(parent[v])
        return parent[v]
    
    def union(v1, v2):
        r1, r2 = find(v1), find(v2)
        if r1 == r2:
            return False
        parent[r2] = r1
        return True
    
    #MST
    mst = {v: [] for v in vertices}
    total = 0
    
    for weight, v1, v2 in edges:
        if union(v1, v2):
            mst[v1].append((v2, weight))
            mst[v2].append((v1, weight))
            total += weight
            if len([v for v in mst if mst[v]]) == len(vertices):
                break
    
    return mst, total

def plot_graph(map_file, graph, vertices, edges_to_draw, output, title, color='b'):
    obstacles = read_map(map_file)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Obstáculos
    for obs in obstacles:
        ax.add_patch(Polygon(obs, closed=True, facecolor='lightgray', 
                            edgecolor='black', linewidth=2))
    
    # Arestas
    drawn = set()
    for v1 in edges_to_draw:
        for v2, _ in edges_to_draw[v1]:
            edge = tuple(sorted([v1, v2]))
            if edge not in drawn:
                ax.plot([v1[0], v2[0]], [v1[1], v2[1]], 
                       color=color, alpha=0.5, linewidth=1.5)
                drawn.add(edge)
    
    # Vértices com coordenadas
    for v in vertices:
        ax.plot(v[0], v[1], 'ro', markersize=5)
        
        ax.text(v[0], v[1] + 15,
                f'({v[0]:.0f},{v[1]:.0f})',
                fontsize=8,
                ha='center',
                va='bottom',
                bbox=dict(boxstyle='round,pad=0.3',
                         facecolor='white',
                         edgecolor='none',
                         alpha=0.7))
    
    ax.set_title(title)
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()

def save_tree_to_file(mst, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Árvore Geradora Mínima (MST) - Formato: vértice: [(vizinho, peso), ...]\n")
        f.write("# Cada linha representa um vértice e suas conexões\n\n")
        
        for vertice in sorted(mst.keys()):
            conexoes = ", ".join([f"({viz[0]}, {viz[1]:.2f})" for viz in mst[vertice]])
            
            f.write(f"{vertice}: [{conexoes}]\n")

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

if __name__ == "__main__":
    MAP_FILE = '../mapa/map.txt'
    MST_FILE = '../mapa/mst_tree.txt'
    
    graph, vertices = create_visibility_graph(MAP_FILE)
    plot_graph(MAP_FILE, graph, vertices, graph, 'visibility_graph.png', 
               'Grafo de Visibilidade', 'b')
    print("Gerado: visibility_graph.png")
    
    mst, total_weight = kruskal_mst(graph, vertices)
    plot_graph(MAP_FILE, graph, vertices, mst, 'mst_kruskal.png', 
               'Árvore Geradora Mínima (Kruskal)', 'g')
    print("Gerado: mst_kruskal.png")
    
    save_tree_to_file(mst, MST_FILE)
