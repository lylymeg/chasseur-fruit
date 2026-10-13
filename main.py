import pygame
import random
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chasseur de Fruits Arcade")
clock = pygame.time.Clock()

# Couleurs (Thème Jungle Néon)
DARK_BG = (15, 25, 20)
GROUND_COLOR = (45, 90, 45)
PLATFORM_COLOR = (60, 120, 60)
PLAYER_COLOR = (0, 255, 157)   # Vert néon
FRUIT_COLOR = (255, 75, 75)    # Rouge (Pomme)
ENEMY_COLOR = (255, 150, 0)    # Orange (Ennemi)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

# Polices
font_large = pygame.font.SysFont("Arial", 42, bold=True)
font_medium = pygame.font.SysFont("Arial", 26, bold=True)
font_small = pygame.font.SysFont("Arial", 18)

def spawn_fruit():
    return {
        "rect": pygame.Rect(random.randint(50, WIDTH - 70), random.randint(100, 320), 24, 24),
        "type": random.choice(["apple", "cherry"])
    }

def create_platforms():
    return [
        pygame.Rect(0, HEIGHT - 60, WIDTH, 60),      # Sol principal
        pygame.Rect(120, 360, 160, 20),              # Plateforme bas-gauche
        pygame.Rect(420, 310, 180, 20),              # Plateforme milieu-droite
        pygame.Rect(250, 220, 200, 20)               # Plateforme haute-centre
    ]

def create_enemies():
    return [
        {"rect": pygame.Rect(150, 330, 30, 30), "speed": 2, "min_x": 120, "max_x": 250},
        {"rect": pygame.Rect(450, 280, 30, 30), "speed": -2, "min_x": 420, "max_x": 570}
    ]

def reset_game():
    return {
        "player": pygame.Rect(100, HEIGHT - 130, 30, 40),
        "dx": 0,
        "dy": 0,
        "on_ground": False,
        "platforms": create_platforms(),
        "enemies": create_enemies(),
        "fruits": [spawn_fruit() for _ in range(4)],
        "score": 0,
        "lives": 3,
        "game_over": False
    }

game = reset_game()
high_score = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game["game_over"]:
                if event.key == pygame.K_SPACE:
                    game = reset_game()
            else:
                if event.key == pygame.K_SPACE and game["on_ground"]:
                    game["dy"] = -12  # Puissance du saut
                    game["on_ground"] = False

    screen.fill(DARK_BG)

    if not game["game_over"]:
        # 1. Contrôles horizontaux (Gauche / Droite ou Q / D)
        keys = pygame.key.get_pressed()
        game["dx"] = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            game["dx"] = -5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            game["dx"] = 5

        # Mouvement horizontal + collisions des bords
        game["player"].x += game["dx"]
        if game["player"].left < 0:
            game["player"].left = 0
        elif game["player"].right > WIDTH:
            game["player"].right = WIDTH

        # 2. Gravité et mouvement vertical
        game["dy"] += 0.5  # Gravité
        game["player"].y += int(game["dy"])

        # Collisions avec les plateformes et le sol
        game["on_ground"] = False
        for plat in game["platforms"]:
            if game["player"].colliderect(plat):
                # Si le joueur tombe sur la plateforme
                if game["dy"] > 0 and game["player"].bottom - game["dy"] <= plat.top + 5:
                    game["player"].bottom = plat.top
                    game["dy"] = 0
                    game["on_ground"] = True

        # Limite haute de l'écran
        if game["player"].top < 0:
            game["player"].top = 0
            game["dy"] = 0

        # 3. Déplacement des ennemis et collisions
        for enemy in game["enemies"]:
            enemy["rect"].x += enemy["speed"]
            if enemy["rect"].left <= enemy["min_x"] or enemy["rect"].right >= enemy["max_x"]:
                enemy["speed"] *= -1

            # Collision Joueur vs Ennemi
            if game["player"].colliderect(enemy["rect"]):
                game["lives"] -= 1
                if game["lives"] <= 0:
                    game["game_over"] = True
                else:
                    # Repositionner le joueur
                    game["player"].x = 100
                    game["player"].y = HEIGHT - 130

        # 4. Collecte des fruits
        for fruit in game["fruits"][:]:
            if game["player"].colliderect(fruit["rect"]):
                game["score"] += 15
                game["fruits"].remove(fruit)
                game["fruits"].append(spawn_fruit())
                if game["score"] > high_score:
                    high_score = game["score"]

        # 5. Dessin du décor (Sol et plateformes)
        for i, plat in enumerate(game["platforms"]):
            color = GROUND_COLOR if i == 0 else PLATFORM_COLOR
            pygame.draw.rect(screen, color, plat, border_radius=4)

        # Dessin des fruits
        for fruit in game["fruits"]:
            pygame.draw.ellipse(screen, FRUIT_COLOR, fruit["rect"])

        # Dessin des ennemis
        for enemy in game["enemies"]:
            pygame.draw.rect(screen, ENEMY_COLOR, enemy["rect"], border_radius=6)

        # Dessin du joueur
        pygame.draw.rect(screen, PLAYER_COLOR, game["player"], border_radius=6)

        # 6. Affichage du HUD (Score et Vies)
        score_txt = font_medium.render(f"Score : {game['score']}", True, WHITE)
        lives_txt = font_medium.render(f"Vies : {'❤️' * game['lives']}", True, WHITE)
        screen.blit(score_txt, (20, 15))
        screen.blit(lives_txt, (WIDTH - lives_txt.get_width() - 20, 15))

    else:
        # Écran Game Over
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        go_title = font_large.render("GAME OVER", True, FRUIT_COLOR)
        final_txt = font_medium.render(f"Score final : {game['score']}", True, WHITE)
        best_txt = font_medium.render(f"Meilleur score : {high_score}", True, PLAYER_COLOR)
        restart_txt = font_small.render("Appuie sur ESPACE pour rejouer", True, GRAY)

        screen.blit(go_title, (WIDTH // 2 - go_title.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(final_txt, (WIDTH // 2 - final_txt.get_width() // 2, HEIGHT // 2 + 15))
        screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 65))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()