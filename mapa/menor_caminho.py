import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math
import heapq

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

def create_visibility_graph(map_file, start=None, goal=None):
    obstacles = read_map(map_file)
    vertices = list(set(v for obs in obstacles for v in obs))
    
    # Adiciona start e goal aos vértices se fornecidos
    if start:
        vertices.append(start)
    if goal:
        vertices.append(goal)
    
    graph = {v: [] for v in vertices}
    
    for i, v1 in enumerate(vertices):
        for v2 in vertices[i+1:]:
            if is_visible(v1, v2, obstacles):
                dist = distance(v1, v2)
                graph[v1].append((v2, dist))
                graph[v2].append((v1, dist))
    
    return graph, vertices, obstacles

def dijkstra(graph, start, goal):
    """
    Algoritmo de Dijkstra para encontrar o caminho mais curto
    """
    # Fila de prioridade: (distância, vértice)
    pq = [(0, start)]
    
    # Dicionários para distâncias e predecessores
    distances = {v: float('inf') for v in graph}
    distances[start] = 0
    predecessors = {v: None for v in graph}
    visited = set()
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
            
        visited.add(current)
        
        # Se chegou ao objetivo, pode parar
        if current == goal:
            break
        
        # Explora vizinhos
        for neighbor, weight in graph[current]:
            if neighbor in visited:
                continue
                
            new_dist = current_dist + weight
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
    
    # Reconstrói o caminho
    if distances[goal] == float('inf'):
        return None, float('inf')
    
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = predecessors[current]
    path.reverse()
    
    return path, distances[goal]

def plot_path(map_file, path, start, goal, output='shortest_path.png'):
    obstacles = read_map(map_file)
    
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Obstáculos
    for obs in obstacles:
        ax.add_patch(Polygon(obs, closed=True, facecolor='lightgray', 
                            edgecolor='black', linewidth=2))
    
    # Vértices dos obstáculos
    vertices = list(set(v for obs in obstacles for v in obs))
    for v in vertices:
        ax.plot(v[0], v[1], 'ko', markersize=4, alpha=0.5)
    
    # Caminho mais curto
    if path:
        for i in range(len(path) - 1):
            ax.plot([path[i][0], path[i+1][0]], 
                   [path[i][1], path[i+1][1]], 
                   'b-', linewidth=3, alpha=0.7, label='Caminho' if i == 0 else '')
        
        # Pontos intermediários do caminho
        for i, p in enumerate(path[1:-1], 1):
            ax.plot(p[0], p[1], 'bo', markersize=8)
            ax.text(p[0], p[1] + 20, f'P{i}', fontsize=9, ha='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))
    
    # Ponto inicial (verde)
    ax.plot(start[0], start[1], 'go', markersize=15, label='Início', zorder=5)
    ax.text(start[0], start[1] - 30, f'Início\n({start[0]:.0f}, {start[1]:.0f})', 
           fontsize=10, ha='center', weight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.9))
    
    # Ponto final (vermelho)
    ax.plot(goal[0], goal[1], 'ro', markersize=15, label='Destino', zorder=5)
    ax.text(goal[0], goal[1] - 30, f'Destino\n({goal[0]:.0f}, {goal[1]:.0f})', 
           fontsize=10, ha='center', weight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.9))
    
    ax.legend(loc='upper right', fontsize=11)
    ax.set_title('Caminho Mais Curto usando Algoritmo de Dijkstra', fontsize=14, weight='bold')
    
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Imagem salva: {output}")

def find_shortest_path(map_file, start, goal):
    """
    Função principal para encontrar o caminho mais curto
    """
    print(f"\n{'='*60}")
    print(f"Buscando caminho mais curto")
    print(f"Início: ({start[0]:.1f}, {start[1]:.1f})")
    print(f"Destino: ({goal[0]:.1f}, {goal[1]:.1f})")
    print(f"{'='*60}\n")
    
    # Cria o grafo de visibilidade incluindo start e goal
    graph, vertices, obstacles = create_visibility_graph(map_file, start, goal)
    
    # Executa Dijkstra
    path, total_distance = dijkstra(graph, start, goal)
    
    if path is None:
        print("❌ Não foi possível encontrar um caminho!")
        return None, None
    
    print(f"✓ Caminho encontrado!")
    print(f"  Distância total: {total_distance:.2f} unidades")
    print(f"  Número de segmentos: {len(path) - 1}")
    print(f"\n  Sequência de pontos:")
    for i, point in enumerate(path):
        if i == 0:
            print(f"    {i}. Início: ({point[0]:.1f}, {point[1]:.1f})")
        elif i == len(path) - 1:
            print(f"    {i}. Destino: ({point[0]:.1f}, {point[1]:.1f})")
        else:
            print(f"    {i}. Ponto {i}: ({point[0]:.1f}, {point[1]:.1f})")
    
    print(f"\n{'='*60}\n")
    
    return path, total_distance


if __name__ == "__main__":
    MAP_FILE = '../mapa/map.txt'
    
    print("\n" + "="*60)
    print("  BUSCADOR DE CAMINHO MÍNIMO")
    print("  Espaço: 0 a 1000 (x e y)")
    print("="*60 + "\n")
    
    while True:
        # Input do ponto inicial
        print("Ponto Inicial:")
        start_x = float(input("  Digite X inicial (0-1000): "))
        start_y = float(input("  Digite Y inicial (0-1000): "))
        start = (start_x, start_y)
        
        # Input do ponto final
        print("\nPonto Destino:")
        goal_x = float(input("  Digite X destino (0-1000): "))
        goal_y = float(input("  Digite Y destino (0-1000): "))
        goal = (goal_x, goal_y)
        
        path, distance = find_shortest_path(MAP_FILE, start, goal)
        
        if path:
            output_file = 'shortest_path.png'
            plot_path(MAP_FILE, path, start, goal, output_file)
            print(f"Visualização salva em: {output_file}")
        else:
            print("\nNão foi possível encontrar um caminho válido!")
            
    