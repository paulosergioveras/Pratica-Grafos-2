import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

def read_map(file):
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
                vertices.append([x, y])
                i += 1
            obstacles.append(vertices)
        else:
            i += 1
    
    return obstacles

def create_map_image(file_txt, file_png):
    obstacles = read_map(file_txt)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    for obs in obstacles:
        polygon = Polygon(obs, closed=True, 
                          facecolor='gray', 
                          edgecolor='black', 
                          linewidth=2)
        ax.add_patch(polygon)
        
        for vertice in obs:
            ax.plot(vertice[0], vertice[1], 'ro', markersize=5)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Map with Obstacles')
    
    plt.savefig(file_png, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Image save in: {file_png}")

create_map_image('mapa/map.txt', 'map.png')
