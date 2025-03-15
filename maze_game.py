import pygame
from random import choice
from collections import deque

# Initialize pygame
pygame.init()

# Game constants
RES = WIDTH, HEIGHT = 1000, 700
TILE = 100
cols, rows = WIDTH // TILE, HEIGHT // TILE
end_point = (cols - 1, rows - 1)  # Bottom-right corner
FPS = 60


class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.thickness = 8  # Thicker walls

    def draw(self, sc):
        x, y = self.x * TILE, self.y * TILE
        if self.walls['top']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y), (x + TILE, y), self.thickness)
        if self.walls['right']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x + TILE, y), (x + TILE, y + TILE), self.thickness)
        if self.walls['bottom']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x + TILE, y + TILE), (x, y + TILE), self.thickness)
        if self.walls['left']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y + TILE), (x, y), self.thickness)

    def get_rects(self):
        rects = []
        x, y = self.x * TILE, self.y * TILE
        if self.walls['top']:
            rects.append(pygame.Rect((x, y), (TILE, self.thickness)))
        if self.walls['right']:
            rects.append(pygame.Rect((x + TILE, y), (self.thickness, TILE)))
        if self.walls['bottom']:
            rects.append(pygame.Rect((x, y + TILE), (TILE, self.thickness)))
        if self.walls['left']:
            rects.append(pygame.Rect((x, y), (self.thickness, TILE)))
        return rects

    def check_cell(self, x, y, grid_cells):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x >= cols or y < 0 or y >= rows:
            return False
        return grid_cells[find_index(x, y)]

    def check_neighbors(self, grid_cells):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1, grid_cells)
        right = self.check_cell(self.x + 1, self.y, grid_cells)
        bottom = self.check_cell(self.x, self.y + 1, grid_cells)
        left = self.check_cell(self.x - 1, self.y, grid_cells)

        if top and not top.visited: neighbors.append(top)
        if right and not right.visited: neighbors.append(right)
        if bottom and not bottom.visited: neighbors.append(bottom)
        if left and not left.visited: neighbors.append(left)
        return choice(neighbors) if neighbors else False


def initialize_game():
    global maze, path, directions, player_rect, current_dir, game_active, stopwatch
    maze = generate_maze()
    path = find_shortest_path(maze)
    directions = get_directions(path)
    player_rect = pygame.Rect(TILE // 2 - 15, TILE // 2 - 15, 30, 30)  # Smaller player
    current_dir = (0, 0)
    game_active = True
    stopwatch = Stopwatch()


def find_current_path():
    px, py = player_rect.centerx // TILE, player_rect.centery // TILE
    return find_shortest_path(maze, (px, py), end_point)


def get_next_direction():
    current_path = find_current_path()
    if len(current_path) < 2: return ""
    dx = current_path[1][0] - current_path[0][0]
    dy = current_path[1][1] - current_path[0][1]
    return {
        (1, 0): 'RIGHT',
        (-1, 0): 'LEFT',
        (0, 1): 'DOWN',
        (0, -1): 'UP'
    }.get((dx, dy), '')


def draw_interface(screen, stopwatch, next_dir):
    # Draw stopwatch
    time_text = pygame.font.SysFont('Arial', 40).render(
        f"Time: {stopwatch.format_time()}", True, pygame.Color('white'))
    screen.blit(time_text, (20, 20))

    # Draw direction suggestion
    dir_text = pygame.font.SysFont('Arial', 60).render(
        f"Next: {next_dir}", True, pygame.Color('limegreen'))
    screen.blit(dir_text, (WIDTH // 2 - 100, 20))


def draw_end_screen(screen, stopwatch):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    text = pygame.font.SysFont('Arial', 80).render("MAZE SOLVED!", True, pygame.Color('yellow'))
    time_text = pygame.font.SysFont('Arial', 60).render(
        f"Time: {stopwatch.format_time()}", True, pygame.Color('yellow'))
    restart_text = pygame.font.SysFont('Arial', 40).render(
        "Press R to restart", True, pygame.Color('white'))

    screen.blit(text, (WIDTH // 2 - 250, HEIGHT // 2 - 60))
    screen.blit(time_text, (WIDTH // 2 - 150, HEIGHT // 2 + 40))
    screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 120))


def handle_movement():
    global current_dir
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: current_dir = (-5, 0)
    if keys[pygame.K_d]: current_dir = (5, 0)
    if keys[pygame.K_w]: current_dir = (0, -5)
    if keys[pygame.K_s]: current_dir = (0, 5)


def move_player():
    if game_active and current_dir != (0, 0):
        new_pos = player_rect.move(current_dir)
        if not new_pos.collidelist(walls_collide_list) != -1:
            player_rect.move_ip(current_dir)



def remove_walls(current, next):
    dx = current.x - next.x
    dy = current.y - next.y
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False


def generate_maze():
    grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
    current_cell = grid_cells[0]
    stack = []
    visited_count = 1

    while visited_count < len(grid_cells):
        current_cell.visited = True
        next_cell = current_cell.check_neighbors(grid_cells)

        if next_cell:
            next_cell.visited = True
            visited_count += 1
            stack.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()
    return grid_cells


def find_shortest_path(maze_grid, start=(0, 0), end=end_point):
    queue = deque([[start]])
    visited = set(start)

    while queue:
        path = queue.popleft()
        x, y = path[-1]

        if (x, y) == end:
            return path

        current_index = x + y * cols
        current_cell = maze_grid[current_index]

        neighbors = []
        if not current_cell.walls['right']: neighbors.append((x + 1, y))
        if not current_cell.walls['left']: neighbors.append((x - 1, y))
        if not current_cell.walls['bottom']: neighbors.append((x, y + 1))
        if not current_cell.walls['top']: neighbors.append((x, y - 1))

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []


def get_directions(path):
    directions = []
    for i in range(1, len(path)):
        px, py = path[i - 1]
        nx, ny = path[i]
        if nx > px:
            directions.append('RIGHT')
        elif nx < px:
            directions.append('LEFT')
        elif ny > py:
            directions.append('DOWN')
        elif ny < py:
            directions.append('UP')
    return directions


class Stopwatch:
    def __init__(self):
        self.start_time = pygame.time.get_ticks()
        self.elapsed = 0
        self.running = True

    def get_time(self):
        if self.running:
            self.elapsed = pygame.time.get_ticks() - self.start_time
        return self.elapsed

    def format_time(self):
        ms = self.get_time()
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02}:{s:02}"



def main():
    global game_active, walls_collide_list

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    initialize_game()

    while True:
        screen.fill(pygame.Color('black'))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if not game_active and event.key == pygame.K_r:
                    initialize_game()

        if game_active:
            handle_movement()
            move_player()

            # Update collisions and path
            walls_collide_list = sum([cell.get_rects() for cell in maze], [])
            if player_rect.colliderect(pygame.Rect(end_point[0] * TILE, end_point[1] * TILE, TILE, TILE)):
                game_active = False
                stopwatch.running = False

        # Draw maze
        for cell in maze:
            cell.draw(screen)

        # Draw player and endpoint
        pygame.draw.rect(screen, pygame.Color('red'),
                         (end_point[0] * TILE + 10, end_point[1] * TILE + 10, TILE - 20, TILE - 20))
        pygame.draw.rect(screen, pygame.Color('cyan'), player_rect)

        # Draw current path
        current_path = find_current_path()
        if current_path:
            path_points = [(x * TILE + TILE // 2, y * TILE + TILE // 2) for (x, y) in current_path]
            # pygame.draw.lines(screen, pygame.Color('limegreen'), False, path_points, 3)
            # Draw a dotted line
            for i in range(len(path_points) - 1):
                start = path_points[i]
                end = path_points[i + 1]
                num_dots = int(((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5 // 10)  # Adjust dot spacing
                for j in range(num_dots):
                    t = j / num_dots
                    dot_x = int(start[0] + t * (end[0] - start[0]))
                    dot_y = int(start[1] + t * (end[1] - start[1]))
                    pygame.draw.circle(screen, pygame.Color('limegreen'), (dot_x, dot_y), 2)  # Adjust dot size


        # Draw interface elements
        next_dir = get_next_direction() if game_active else ""
        draw_interface(screen, stopwatch, next_dir)

        if not game_active:
            draw_end_screen(screen, stopwatch)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
