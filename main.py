import pygame
import random
import math

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Caixeiro Viajante - Ant Colony Optimization")
clock = pygame.time.Clock()

# Parâmetros ACO
TOTAL_CITIES = 10
NUM_ANTS = 20
EVAPORATION_RATE = 0.5
ALPHA = 1.0  # Importância do feromônio
BETA = 2.0   # Importância da heurística (distância)
Q = 100      # Constante de deposição de feromônio

# Variáveis globais
cities = []
pheromone = []
distance_matrix = []
record_distance = float('inf')
best_ever = []
current_best = []
iteration_count = 0
execution_number = 1

# Estatísticas para a tabela
stats = {
    'execution': execution_number,
    'evaporation_rate': EVAPORATION_RATE,
    'num_ants': NUM_ANTS,
    'alpha': ALPHA,
    'beta': BETA,
    'iterations': 0,
    'best_distance': float('inf')
}

# Funções auxiliares
def calc_distance_between(city_a, city_b):
    return math.dist(city_a, city_b)

def calc_distance(points, order):
    sum_dist = 0
    for i in range(len(order) - 1):
        city_a_index = order[i]
        city_a = points[city_a_index]
        city_b_index = order[i + 1]
        city_b = points[city_b_index]
        d = calc_distance_between(city_a, city_b)
        sum_dist += d
    # Adiciona a distância de volta para a cidade inicial
    last_city = points[order[-1]]
    first_city = points[order[0]]
    sum_dist += calc_distance_between(last_city, first_city)
    return sum_dist

# Inicializa a matriz de feromônios
def init_pheromone():
    global pheromone
    pheromone = [[1.0 for _ in range(TOTAL_CITIES)] for _ in range(TOTAL_CITIES)]

# Inicializa a matriz de distâncias
def init_distance_matrix():
    global distance_matrix
    distance_matrix = [[0.0 for _ in range(TOTAL_CITIES)] for _ in range(TOTAL_CITIES)]
    for i in range(TOTAL_CITIES):
        for j in range(TOTAL_CITIES):
            if i != j:
                distance_matrix[i][j] = calc_distance_between(cities[i], cities[j])

# Seleciona a próxima cidade baseado em feromônio e heurística
def select_next_city(current_city, unvisited):
    probabilities = []
    total = 0.0
    
    for city in unvisited:
        pheromone_level = pheromone[current_city][city] ** ALPHA
        distance = distance_matrix[current_city][city]
        heuristic = (1.0 / distance) ** BETA if distance > 0 else 0
        prob = pheromone_level * heuristic
        probabilities.append(prob)
        total += prob
    
    if total == 0:
        return random.choice(unvisited)
    
    # Normaliza as probabilidades
    probabilities = [p / total for p in probabilities]
    
    # Seleção por roleta
    r = random.random()
    cumulative = 0.0
    for i, prob in enumerate(probabilities):
        cumulative += prob
        if r <= cumulative:
            return unvisited[i]
    
    return unvisited[-1]

# Constrói uma solução para uma formiga
def construct_solution():
    start_city = random.randint(0, TOTAL_CITIES - 1)
    tour = [start_city]
    unvisited = [i for i in range(TOTAL_CITIES) if i != start_city]
    
    current_city = start_city
    while unvisited:
        next_city = select_next_city(current_city, unvisited)
        tour.append(next_city)
        unvisited.remove(next_city)
        current_city = next_city
    
    return tour

# Evapora os feromônios
def evaporate_pheromones():
    global pheromone
    for i in range(TOTAL_CITIES):
        for j in range(TOTAL_CITIES):
            pheromone[i][j] *= (1 - EVAPORATION_RATE)

# Deposita feromônios baseado nas soluções das formigas
def deposit_pheromones(ant_tours, ant_distances):
    for tour, distance in zip(ant_tours, ant_distances):
        pheromone_deposit = Q / distance
        for i in range(len(tour) - 1):
            city_a = tour[i]
            city_b = tour[i + 1]
            pheromone[city_a][city_b] += pheromone_deposit
            pheromone[city_b][city_a] += pheromone_deposit

# Executa uma iteração do ACO
def run_aco_iteration():
    global record_distance, best_ever, current_best, iteration_count, stats
    
    ant_tours = []
    ant_distances = []
    
    # Cada formiga constrói uma solução
    for _ in range(NUM_ANTS):
        tour = construct_solution()
        distance = calc_distance(cities, tour)
        ant_tours.append(tour)
        ant_distances.append(distance)
        
        # Atualiza o melhor de todos os tempos
        if distance < record_distance:
            record_distance = distance
            best_ever = tour.copy()
            stats['best_distance'] = distance
    
    # Encontra o melhor da iteração atual
    min_distance = min(ant_distances)
    min_index = ant_distances.index(min_distance)
    current_best = ant_tours[min_index].copy()
    
    # Evapora feromônios
    evaporate_pheromones()
    
    # Deposita novos feromônios
    deposit_pheromones(ant_tours, ant_distances)
    
    iteration_count += 1
    stats['iterations'] = iteration_count

# Setup inicial
def setup():
    global cities
    for i in range(TOTAL_CITIES):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT // 2 - 50)
        cities.append((x, y))
    
    init_distance_matrix()
    init_pheromone()

def print_stats():
    print(f"\n{'='*70}")
    print(f"RESULTADOS DA EXECUÇÃO")
    print(f"{'='*70}")
    print(f"N° Execução: {stats['execution']}")
    print(f"Taxa de Evaporação: {stats['evaporation_rate']:.2f}")
    print(f"Número de Formigas: {stats['num_ants']}")
    print(f"Alpha (Feromônio): {stats['alpha']:.2f}")
    print(f"Beta (Heurística): {stats['beta']:.2f}")
    print(f"N° de Iterações: {stats['iterations']}")
    print(f"Melhor Distância: {stats['best_distance']:.2f}")
    print(f"{'='*70}\n")

# Função de desenho
def draw():
    screen.fill((0, 0, 0))
    
    # Executa uma iteração do ACO
    run_aco_iteration()
    
    # Desenha o melhor caminho de todos os tempos (metade superior)
    if best_ever:
        # Desenha as linhas
        for i in range(len(best_ever) - 1):
            n = best_ever[i]
            n_next = best_ever[i + 1]
            pygame.draw.line(screen, (255, 0, 0), cities[n], cities[n_next], 2)
        # Linha de volta para a cidade inicial
        pygame.draw.line(screen, (255, 0, 0), cities[best_ever[-1]], cities[best_ever[0]], 2)
        
        # Desenha os círculos nas cidades
        for i in range(len(best_ever)):
            n = best_ever[i]
            pygame.draw.circle(screen, (255, 255, 255), cities[n], 8, 2)
    
    # Desenha o melhor caminho da iteração atual (metade inferior)
    if current_best:
        # Desenha as linhas
        for i in range(len(current_best) - 1):
            n = current_best[i]
            n_next = current_best[i + 1]
            city_a = (cities[n][0], cities[n][1] + HEIGHT // 2)
            city_b = (cities[n_next][0], cities[n_next][1] + HEIGHT // 2)
            pygame.draw.line(screen, (0, 255, 0), city_a, city_b, 2)
        # Linha de volta para a cidade inicial
        last_city = (cities[current_best[-1]][0], cities[current_best[-1]][1] + HEIGHT // 2)
        first_city = (cities[current_best[0]][0], cities[current_best[0]][1] + HEIGHT // 2)
        pygame.draw.line(screen, (0, 255, 0), last_city, first_city, 2)
        
        # Desenha os círculos nas cidades
        for i in range(len(current_best)):
            n = current_best[i]
            city = (cities[n][0], cities[n][1] + HEIGHT // 2)
            pygame.draw.circle(screen, (255, 255, 255), city, 8, 2)
    
    # Exibe informações
    font = pygame.font.Font(None, 28)
    text1 = font.render(f"Iteracao: {iteration_count}", True, (255, 255, 255))
    text2 = font.render(f"Melhor Distancia: {record_distance:.2f}", True, (255, 255, 255))
    screen.blit(text1, (10, 10))
    screen.blit(text2, (10, 40))
    
    pygame.display.flip()

# Loop principal
def main():
    setup()
    running = True
    
    print("\n" + "="*60)
    print("ANT COLONY OPTIMIZATION - PROBLEMA DO CAIXEIRO VIAJANTE")
    print("="*60)
    print(f"Configurações:")
    print(f" - Número de Cidades: {TOTAL_CITIES}")
    print(f" - Número de Formigas: {NUM_ANTS}")
    print(f" - Taxa de Evaporação: {EVAPORATION_RATE}")
    print(f" - Alpha (Feromônio): {ALPHA}")
    print(f" - Beta (Heurística): {BETA}")
    print(f"\nPressione ESC para finalizar e salvar resultados")
    print("="*60 + "\n")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print_stats()
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print_stats()
                    running = False
        
        draw()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()

if __name__ == "__main__":
    main()
