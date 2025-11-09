import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math

def read_map(file):
    """Lê o arquivo de mapa e retorna lista de obstáculos"""
    obstacles = []
    with open(file, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        linha = lines[i].strip()
        if linha == 'OBSTACLE':
            i += 1
            num_vertices = int(lines[i].strip())
            i += 1
            vertices = []
            for j in range(num_vertices):
                x, y = map(float, lines[i].split(','))
                vertices.append((x, y))
                i += 1
            obstacles.append(vertices)
        else:
            i += 1
    
    return obstacles

def ccw(A, B, C):
    """Retorna True se os pontos A, B, C estão em sentido anti-horário"""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

def segments_intersect(A, B, C, D):
    """Verifica se o segmento AB intersecta o segmento CD"""
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def point_in_polygon(point, polygon):
    """Verifica se um ponto está dentro de um polígono usando ray casting"""
    x, y = point
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside

def is_visible(p1, p2, obstacles):
    """Verifica se existe linha de visão entre p1 e p2"""
    # Verifica se o segmento intersecta alguma aresta dos obstáculos
    for obstacle in obstacles:
        n = len(obstacle)
        for i in range(n):
            edge_start = obstacle[i]
            edge_end = obstacle[(i + 1) % n]
            
            # Ignora se p1 ou p2 são vértices da aresta
            if (p1 == edge_start or p1 == edge_end or 
                p2 == edge_start or p2 == edge_end):
                continue
            
            if segments_intersect(p1, p2, edge_start, edge_end):
                return False
    
    # Verifica se o ponto médio está dentro de algum obstáculo
    mid_point = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    for obstacle in obstacles:
        if point_in_polygon(mid_point, obstacle):
            return False
    
    return True

def euclidean_distance(p1, p2):
    """Calcula a distância euclidiana entre dois pontos"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def create_visibility_graph(map_file):

    obstacles = read_map(map_file)
    
    # Extrai todos os vértices dos obstáculos
    vertices = []
    for obstacle in obstacles:
        vertices.extend(obstacle)
    
    # Remove duplicatas
    vertices = list(set(vertices))
    
    print(f"Total de vértices: {len(vertices)}")
    
    # Cria o grafo
    graph = {v: [] for v in vertices}
    
    # Para cada par de vértices, verifica visibilidade
    total_edges = 0
    for i, v1 in enumerate(vertices):
        for j, v2 in enumerate(vertices):
            if i >= j:  # Evita duplicatas e auto-loops
                continue
            
            if is_visible(v1, v2, obstacles):
                distance = euclidean_distance(v1, v2)
                graph[v1].append((v2, distance))
                graph[v2].append((v1, distance))
                total_edges += 1
    
    print(f"Total de arestas: {total_edges}")
    
    return graph, vertices

def visualize_visibility_graph(map_file, graph, vertices, output_file='visibility_graph.png'):
    """Visualiza o grafo de visibilidade sobre o mapa"""
    obstacles = read_map(map_file)
    
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Desenha obstáculos
    for obs in obstacles:
        polygon = Polygon(obs, closed=True, 
                          facecolor='lightgray', 
                          edgecolor='black', 
                          linewidth=2)
        ax.add_patch(polygon)
    
    # Desenha arestas do grafo de visibilidade
    drawn_edges = set()
    for v1 in graph:
        for v2, weight in graph[v1]:
            edge = tuple(sorted([v1, v2]))
            if edge not in drawn_edges:
                ax.plot([v1[0], v2[0]], [v1[1], v2[1]], 
                       'b-', alpha=0.3, linewidth=0.5)
                drawn_edges.add(edge)
    
    # Desenha vértices
    for v in vertices:
        ax.plot(v[0], v[1], 'ro', markersize=4)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Grafo de Visibilidade')
    
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Grafo salvo em: {output_file}")


if __name__ == "__main__":
    graph, vertices = create_visibility_graph('mapa/map.txt')
    visualize_visibility_graph('mapa/map.txt', graph, vertices)
    