import random
import pygame

WIDTH, HEIGHT = 640, 480


class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT - 40, 32, 32)
        self.vy = 0
        self.on_ground = True
        self.lives = 3

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

    def jump(self):
        if self.on_ground:
            self.vy = -12
            self.on_ground = False

    def take_hit(self):
        self.lives -= 1


def spawn_rock():
    return pygame.Rect(random.randint(0, WIDTH - 20), -20, 20, 20)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    player = Player()
    rocks = []
    score = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.jump()
        player.handle_input(pygame.key.get_pressed())
        if random.random() < 0.03:
            rocks.append(spawn_rock())
        for rock in rocks[:]:
            rock.y += 4
            if rock.colliderect(player.rect):
                player.take_hit()
                rocks.remove(rock)
        score += 1
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), player.rect)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
