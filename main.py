import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 900, 600
FPS = 60
ROAD_COLOR = (50, 50, 50)
BG_COLOR = (34, 177, 76)
BUTTON_COLOR = (60, 60, 60)
BUTTON_HOVER_COLOR = (90, 90, 90)
PANEL_COLOR = (40, 40, 40)
WHITE = (255, 255, 255)
BLACK = (220, 220, 220)
DESTINATION_COLOR = (255, 0, 0)
TREE_COLORS = [(0, 100, 0), (0, 120, 0), (0, 80, 0)]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Self-Driving Car Simulator")
clock = pygame.time.Clock()

try:
    car_img = pygame.image.load("cyber.png").convert_alpha()
    car_img = pygame.transform.scale(car_img, (130, 100))
except:
    car_img = pygame.Surface((70, 50), pygame.SRCALPHA)
    pygame.draw.rect(car_img, (0, 100, 255), (0, 0, 70, 50))
    pygame.draw.polygon(car_img, (200, 200, 200), [(50, 10), (70, 25), (50, 40)])

car_rect = pygame.Rect(110, 160, 70, 50)
car_speed = 3
car_moving = False
destination = None
path = []
current_road = None

roads = [
    pygame.Rect(100, 0, 80, HEIGHT),
    pygame.Rect(300, 0, 80, HEIGHT),
    pygame.Rect(500, 0, 80, HEIGHT),
    pygame.Rect(0, 150, WIDTH-200, 80),
    pygame.Rect(0, 350, WIDTH-200, 80),
    pygame.Rect(150, 200, 200, 80),
    pygame.Rect(350, 300, 200, 80),
]

intersections = [
    (140, 190), (140, 390),
    (340, 190), (340, 390),
    (540, 190), (540, 390),
    (200, 190), (400, 190), (600, 190),
    (200, 390), (400, 390), (600, 390),
    (250, 240), (450, 340),
    (140, 100), (140, 290), (140, 490),
    (340, 100), (340, 290), (340, 490),
    (540, 100), (540, 290), (540, 490),
    (50, 190), (50, 390),
    (650, 190), (650, 390)
]

buildings = []
for _ in range(15):
    size = random.randint(40, 120)
    x = random.randint(0, WIDTH - size)
    y = random.randint(0, HEIGHT - size)
    building_rect = pygame.Rect(x, y, size, size)
    on_road = any(building_rect.colliderect(road) for road in roads)
    if not on_road:
        buildings.append((building_rect, (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))))

trees = []
for _ in range(50):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(15, 30)
    on_road = any(pygame.Rect(x-size//2, y-size//2, size, size).colliderect(road) for road in roads)
    if not on_road:
        trees.append((x, y, size, random.choice(TREE_COLORS)))

obstacles = [
    (270, 390),
]

start_button = pygame.Rect(730, 80, 140, 40)
stop_button = pygame.Rect(730, 140, 140, 40)
dest_button = pygame.Rect(730, 200, 140, 40)

font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)

def draw_road(road_rect):
    pygame.draw.rect(screen, ROAD_COLOR, road_rect, border_radius=10 if road_rect.width > road_rect.height else 0)
    dash_length = 15
    spacing = 10
    if road_rect.width > road_rect.height:
        y = road_rect.centery
        for x in range(road_rect.left, road_rect.right, dash_length + spacing):
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y - 2, dash_length, 4), border_radius=2)
    else:
        x = road_rect.centerx
        for y in range(road_rect.top, road_rect.bottom, dash_length + spacing):
            pygame.draw.rect(screen, WHITE, pygame.Rect(x - 2, y, 4, dash_length), border_radius=2)

def draw_buildings():
    for building, color in buildings:
        pygame.draw.rect(screen, color, building)
        for x in range(building.left + 5, building.right - 5, 15):
            for y in range(building.top + 5, building.bottom - 5, 15):
                if random.random() > 0.3:
                    pygame.draw.rect(screen, (255, 255, 200), pygame.Rect(x, y, 8, 8))

def draw_trees():
    for x, y, size, color in trees:
        pygame.draw.rect(screen, (101, 67, 33), (x-3, y+size//2, 6, size))
        pygame.draw.circle(screen, color, (x, y), size//2)
        pygame.draw.circle(screen, color, (x-size//3, y+size//4), size//2)
        pygame.draw.circle(screen, color, (x+size//3, y+size//4), size//2)

def draw_buttons():
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER_COLOR if start_button.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, start_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, start_button, 2, border_radius=5)
    screen.blit(font.render("Start", True, WHITE), (start_button.x + 45, start_button.y + 10))
    color = BUTTON_HOVER_COLOR if stop_button.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, stop_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, stop_button, 2, border_radius=5)
    screen.blit(font.render("Stop", True, WHITE), (stop_button.x + 48, stop_button.y + 10))
    color = BUTTON_HOVER_COLOR if dest_button.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, dest_button, border_radius=5)
    pygame.draw.rect(screen, BLACK, dest_button, 2, border_radius=5)
    screen.blit(small_font.render("Set Destination", True, WHITE), (dest_button.x + 10, dest_button.y + 10))

def draw_panel():
    panel = pygame.Rect(700, 0, 200, HEIGHT)
    pygame.draw.rect(screen, PANEL_COLOR, panel)
    pygame.draw.rect(screen, BLACK, panel, 2)
    title_font = pygame.font.SysFont('Arial', 30, bold=True)
    screen.blit(title_font.render("Controls", True, WHITE), (740, 30))
    status = "Moving" if car_moving else "Stopped"
    status_color = (0, 150, 0) if car_moving else (150, 0, 0)
    screen.blit(font.render(f"Status: {status}", True, status_color), (720, 260))
    if destination:
        screen.blit(small_font.render(f"Destination:", True, WHITE), (720, 300))
        screen.blit(small_font.render(f"X: {destination[0]}", True, WHITE), (720, 330))
        screen.blit(small_font.render(f"Y: {destination[1]}", True, WHITE), (720, 360))

def draw_obstacles():
    for x, y in obstacles:
        pygame.draw.circle(screen, (255, 0, 0), (x, y), 10)

def check_road_bounds():
    for road in roads:
        if road.collidepoint(car_rect.center):
            return road
    return None

def find_closest_node(pos):
    if not intersections:
        return pos
    closest = min(intersections, key=lambda p: math.dist(pos, p))
    return closest

def find_path(start_pos, end_pos):
    start_node = find_closest_node(start_pos)
    end_node = find_closest_node(end_pos)
    if math.dist(start_pos, end_pos) < 150 and is_same_road_segment(start_pos, end_pos):
        return [start_pos, end_pos]
    graph = create_navigation_graph()
    open_set = {start_node}
    came_from = {}
    g_score = {node: float('inf') for node in intersections}
    g_score[start_node] = 0
    f_score = {node: float('inf') for node in intersections}
    f_score[start_node] = heuristic(start_node, end_node)
    while open_set:
        current = min(open_set, key=lambda node: f_score[node])
        if current == end_node:
            path = [end_pos]
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_pos)
            path.reverse()
            return path
        open_set.remove(current)
        for neighbor in graph.get(current, []):
            tentative_g_score = g_score[current] + math.dist(current, neighbor)
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end_node)
                if neighbor not in open_set:
                    open_set.add(neighbor)
    return [start_pos, end_pos]

def heuristic(node, end_node):
    return math.dist(node, end_node)

def is_same_road_segment(pos1, pos2):
    for road in roads:
        if road.collidepoint(pos1) and road.collidepoint(pos2):
            if road.width > road.height:
                if abs(pos1[1] - pos2[1]) < 20:
                    return True
            else:
                if abs(pos1[0] - pos2[0]) < 20:
                    return True
    return False

def create_navigation_graph():
    graph = {}
    for i, node1 in enumerate(intersections):
        connections = []
        for j, node2 in enumerate(intersections):
            if i != j and is_same_road_segment(node1, node2):
                if math.dist(node1, node2) < 250:
                    connections.append(node2)
        graph[node1] = connections
    return graph

def rotate_car(dx, dy):
    angle = math.degrees(math.atan2(-dy, dx)) - 90
    return pygame.transform.rotate(car_img, angle)

def check_obstacle_avoidance(target_pos, current_pos):
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return None
    dx /= distance
    dy /= distance
    closest_obstacle = None
    closest_distance = float('inf')
    for obstacle in obstacles:
        ox = obstacle[0] - current_pos[0]
        oy = obstacle[1] - current_pos[1]
        dot_product = ox * dx + oy * dy
        if 0 < dot_product < distance:
            projection_x = current_pos[0] + dot_product * dx
            projection_y = current_pos[1] + dot_product * dy
            obstacle_distance = math.hypot(obstacle[0] - projection_x, obstacle[1] - projection_y)
            if obstacle_distance < 20 and obstacle_distance < closest_distance:
                closest_obstacle = obstacle
                closest_distance = obstacle_distance
    if closest_obstacle:
        if abs(dx) > abs(dy):
            return (current_pos[0], current_pos[1] + 30 * (-1 if dy >= 0 else 1))
        else:
            return (current_pos[0] + 30 * (-1 if dx >= 0 else 1), current_pos[1])
    return None

running = True
setting_destination = False
while running:
    screen.fill(BG_COLOR)
    draw_buildings()
    draw_trees()
    for road in roads:
        draw_road(road)
    draw_obstacles()
    draw_panel()
    draw_buttons()
    if destination:
        pygame.draw.circle(screen, DESTINATION_COLOR, destination, 10)
        pygame.draw.circle(screen, WHITE, destination, 5)
    if len(path) > 1:
        pygame.draw.lines(screen, (0, 255, 255, 150), False, path, 3)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                car_moving = True
                if destination and not path:
                    path = find_path(car_rect.center, destination)
            elif stop_button.collidepoint(event.pos):
                car_moving = False
                path = []
            elif dest_button.collidepoint(event.pos):
                setting_destination = True
            elif setting_destination:
                for road in roads:
                    if road.collidepoint(event.pos):
                        destination = event.pos
                        path = find_path(car_rect.center, destination)
                        print(f"Destination set at {destination}")
                        setting_destination = False
                        break
    if car_moving and path:
        target_pos = path[0]
        avoidance_pos = check_obstacle_avoidance(target_pos, car_rect.center)
        if avoidance_pos:
            target_pos = avoidance_pos
        dx = target_pos[0] - car_rect.centerx
        dy = target_pos[1] - car_rect.centery
        distance = math.hypot(dx, dy)
        if distance > car_speed:
            dx /= distance
            dy /= distance
            car_rect.x += dx * car_speed
            car_rect.y += dy * car_speed
        else:
            car_rect.center = target_pos
            if target_pos == path[0]:
                path.pop(0)
                if not path:
                    car_moving = False
    current_road = check_road_bounds()
    if not current_road and not car_moving:
        for road in roads:
            if car_rect.colliderect(road):
                car_rect = car_rect.clamp(road)
                break
    if car_moving and path:
        dx = path[0][0] - car_rect.centerx
        dy = path[0][1] - car_rect.centery
        rotated_car = rotate_car(dx, dy)
        car_rect = rotated_car.get_rect(center=car_rect.center)
        screen.blit(rotated_car, car_rect)
    else:
        screen.blit(car_img, car_rect)
    if setting_destination:
        mouse_pos = pygame.mouse.get_pos()
        on_road = any(road.collidepoint(mouse_pos) for road in roads)
        color = DESTINATION_COLOR if on_road else (255, 100, 100)
        pygame.draw.circle(screen, color, mouse_pos, 10, 2)
        screen.blit(small_font.render("Click on road to set destination", True, BLACK), (mouse_pos[0]+15, mouse_pos[1]-15))
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
