import pygame
import matplotlib.pyplot as plt  # For histogram plotting
from random import choice
from collections import deque
from pyduino_controller import PyduinoController
from pygame import mixer

# Initialize pygame and mixer
pygame.init()
mixer.init()

# Attempt to initialize the Arduino controller.
# If it fails, ARDUINO will be set to None and the game continues without Arduino integration.
try:
    ARDUINO = PyduinoController()
except Exception as e:
    print("Arduino not found or failed to initialize:", e)
    ARDUINO = None

# Game constants
RES = WIDTH, HEIGHT = 900, 700
TILE = 100
cols, rows = WIDTH // TILE, HEIGHT // TILE
end_point = (cols - 1, rows - 1)  # Bottom-right corner
FPS = 60

# SOUND EFFECTS
OUCH_SFX = mixer.Sound('sfx/ouch.mp3')
YAY_SFX = mixer.Sound('sfx/yay.mp3')
# New threshold sounds
THRESHOLD_25_SFX = mixer.Sound('sfx/25.mp3')
THRESHOLD_50_SFX = mixer.Sound('sfx/50.mp3')
THRESHOLD_75_SFX = mixer.Sound('sfx/75.mp3')


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


def get_current_path_completion_percentage(current_path) -> int:
    return 100 - int(round(len(current_path) / len(total_path) * 100))


# --- Functions to save and display completion times ---

def save_completion_time(time_seconds):
    """Append the completion time (in seconds) to a tex file."""
    with open("completion_times.tex", "a") as f:
        f.write(f"{time_seconds}\n")


def load_completion_times():
    """Load all completion times from the tex file."""
    times = []
    try:
        with open("completion_times.tex", "r") as f:
            for line in f:
                try:
                    times.append(float(line.strip()))
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    return times


def show_histogram(current_time):
    """Display a histogram of all completion times with a vertical line for the current time."""
    times = load_completion_times()
    plt.hist(times, bins=10, color='skyblue', edgecolor='black')
    plt.axvline(current_time, color='red', linestyle='dashed', linewidth=2,
                label=f"Current Time: {current_time:.2f}s")
    plt.xlabel("Completion Time (seconds)")
    plt.ylabel("Frequency")
    plt.title("Completion Times Histogram")
    plt.legend()
    plt.show()


# --- Game-related functions ---

def initialize_game():
    global maze, path, directions, player_rect, current_dir, game_active, stopwatch, total_path, time_saved, histogram_shown
    global played_25, played_50, played_75
    maze = generate_maze()
    path = find_shortest_path(maze)
    total_path = path.copy()
    directions = get_directions(path)
    player_rect = pygame.Rect(TILE // 2 - 15, TILE // 2 - 15, 30, 30)  # Smaller player
    current_dir = (0, 0)
    game_active = True
    stopwatch = Stopwatch()
    time_saved = False       # Ensure we save time only once per completion
    histogram_shown = False  # Show histogram only once after game over
    # Initialize threshold flags
    played_25 = False
    played_50 = False
    played_75 = False


def find_current_path():
    px, py = player_rect.centerx // TILE, player_rect.centery // TILE
    return find_shortest_path(maze, (px, py), end_point)


def get_next_direction():
    current_path = find_current_path()
    if len(current_path) < 2:
        return ""
    dx = current_path[1][0] - current_path[0][0]
    dy = current_path[1][1] - current_path[0][1]
    return {
        (1, 0): 'RIGHT',
        (-1, 0): 'LEFT',
        (0, 1): 'DOWN',
        (0, -1): 'UP'
    }.get((dx, dy), '')


def send_direction_to_arduino(direction: str):
    # Only send commands if the ARDUINO is initialized.
    if ARDUINO is None:
        return
    if direction == 'RIGHT':
        ARDUINO.send_command('R')
    elif direction == 'LEFT':
        ARDUINO.send_command('L')
    elif direction == 'UP':
        ARDUINO.send_command('U')
    elif direction == 'DOWN':
        ARDUINO.send_command('D')


def draw_interface(screen, stopwatch, next_dir, percent_complete):
    # Draw stopwatch
    time_text = pygame.font.SysFont('Arial', 40).render(
        f"Time: {stopwatch.format_time()}", True, pygame.Color('white'))
    screen.blit(time_text, (20, 20))

    # Draw direction suggestion
    dir_text = pygame.font.SysFont('Arial', 60).render(
        f"Next: {next_dir}", True, pygame.Color('limegreen'))
    screen.blit(dir_text, (WIDTH // 2 - 100, 20))

    percent_text = pygame.font.SysFont('Arial', 40).render(
        f"Completion: {percent_complete}%", True, pygame.Color('white'))
    screen.blit(percent_text, (WIDTH // 2 - 100, 100))


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

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        print("LEFT")
        current_dir = (-5, 0)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        print("RIGHT")
        current_dir = (5, 0)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        print("UP")
        current_dir = (0, -5)
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        print("DOWN")
        current_dir = (0, 5)


def move_player():
    if game_active and current_dir != (0, 0):
        new_pos = player_rect.move(current_dir)
        if new_pos.collidelist(walls_collide_list) == -1:
            player_rect.move_ip(current_dir)
        # Collision handling (sound effects, etc.) can be added here


def main():
    global game_active, walls_collide_list, time_saved, histogram_shown
    global played_25, played_50, played_75

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    initialize_game()
    yay_played = False

    while True:
        screen.fill(pygame.Color('black'))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if not game_active and event.key == pygame.K_r:
                    initialize_game()
                    yay_played = False

        if game_active:
            handle_movement()
            move_player()

            # Update collisions and path
            walls_collide_list = sum([cell.get_rects() for cell in maze], [])
            # Check for completion (player reaches end point)
            if player_rect.colliderect(pygame.Rect(end_point[0] * TILE, end_point[1] * TILE, TILE, TILE)):
                game_active = False
                stopwatch.running = False
        else:
            # When game ends, save the completion time only once.
            if not time_saved:
                comp_time = stopwatch.get_time() / 1000.0  # Convert milliseconds to seconds
                save_completion_time(comp_time)
                time_saved = True

            draw_end_screen(screen, stopwatch)
            if not yay_played:
                YAY_SFX.play()
                # Only send the finish command if ARDUINO exists.
                if ARDUINO:
                    ARDUINO.send_command('F')
                yay_played = True

            # Show the histogram only once after game completion.
            if not histogram_shown:
                current_time_sec = stopwatch.get_time() / 1000.0
                show_histogram(current_time_sec)
                histogram_shown = True

        # Draw maze
        for cell in maze:
            cell.draw(screen)

        # Draw player and endpoint
        pygame.draw.rect(screen, pygame.Color('red'),
                         (end_point[0] * TILE + 10, end_point[1] * TILE + 10, TILE - 20, TILE - 20))
        pygame.draw.rect(screen, pygame.Color('cyan'), player_rect)

        # Draw current path as a dotted line
        current_path = find_current_path()
        if current_path:
            path_points = [(x * TILE + TILE // 2, y * TILE + TILE // 2) for (x, y) in current_path]
            for i in range(len(path_points) - 1):
                start = path_points[i]
                end = path_points[i + 1]
                num_dots = int(((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5 // 10)
                for j in range(num_dots):
                    t = j / num_dots
                    dot_x = int(start[0] + t * (end[0] - start[0]))
                    dot_y = int(start[1] + t * (end[1] - start[1]))
                    pygame.draw.circle(screen, pygame.Color('limegreen'), (dot_x, dot_y), 2)

        percent_complete = get_current_path_completion_percentage(current_path)
        # Check and play threshold sounds (only once per threshold)
        if not played_25 and percent_complete >= 25:
            THRESHOLD_25_SFX.play()
            played_25 = True
        if not played_50 and percent_complete >= 50:
            THRESHOLD_50_SFX.play()
            played_50 = True
        if not played_75 and percent_complete >= 75:
            THRESHOLD_75_SFX.play()
            played_75 = True

        next_dir = get_next_direction() if game_active else ""
        send_direction_to_arduino(next_dir)
        draw_interface(screen, stopwatch, next_dir, percent_complete)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
