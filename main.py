import pygame, sys, time
from sprites import Background, Bird, Obstacle
from random import randint
from settings import *

pygame.init()

class Game:
    def __init__(self):
        # pygame init
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("flappy block")
        pygame.display.set_icon(pygame.image.load('assets/icon.png'))
        self.active = False
        self.score = 0
        self.start_offset = 0
        self.gap_size = OBSTACLE_GAP_SIZE

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # scale factor
        bg_height = pygame.image.load('assets/background.png').get_height()
        self.scale_factor = SCREEN_HEIGHT / bg_height

        # sprite init
        Background(self.all_sprites, self.scale_factor)

        # timer
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)

        # fonts
        self.score_font = pygame.font.Font('assets/font.ttf', 40)
        self.menu_font = pygame.font.Font('assets/font.ttf', 20)

        # menu, text
        menu_img = pygame.image.load('assets/menu.png').convert_alpha()
        self.menu_surf = pygame.transform.scale(menu_img, pygame.math.Vector2(menu_img.get_size()) * 0.7)
        self.menu_rect = self.menu_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))

        self.menu_text_surf = self.menu_font.render("Press 'space' to start!", False, (255, 255, 255))
        self.menu_text_rect = self.menu_text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.2))

    def display_score(self):
        if self.active:
            self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
            y =  SCREEN_HEIGHT / 15
        else:
            y = SCREEN_HEIGHT / 2 + (self.menu_rect.height / 2)

        score_surf = self.score_font.render(str(self.score), False, (255, 255, 255))
        score_rect = score_surf.get_rect(midtop = (SCREEN_WIDTH / 2, y))
        self.screen.blit(score_surf,score_rect)

    def collision(self):
        if pygame.sprite.spritecollide(self.bird, self.collision_sprites, False, pygame.sprite.collide_mask) or self.bird.rect.centery <= 0 or self.bird.rect.bottom >= SCREEN_HEIGHT:
            self.active = False
            self.gap_size = 350
            self.bird.kill()
            for sprite in self.collision_sprites.sprites():
                sprite.kill()

    def run(self):
        last_time = time.time()
        while True:

            # delta time ?
            dt = time.time() - last_time
            last_time = time.time()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.active:
                        self.bird.jump()
                    else:
                        self.bird = Bird(self.all_sprites, self.scale_factor * 0.4)
                        self.active = True
                        self.start_offset = pygame.time.get_ticks()

                if event.type == self.obstacle_timer and self.active:
                    x = SCREEN_WIDTH + randint(40, 100)
                    yr = randint(50, 250)
                    if self.score in (20, 50, 100):
                        self.gap_size -= 10
                    Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 5, 'top', x, yr, self.gap_size)
                    Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 5, 'bottom', x, yr, self.gap_size)

            # game logic
            self.screen.fill((0, 0, 0))
            self.all_sprites.update(dt)
            self.all_sprites.draw(self.screen)
            self.display_score()

            if self.active:
                self.collision()
            else:
                self.screen.blit(self.menu_surf, self.menu_rect)
                self.screen.blit(self.menu_text_surf, self.menu_text_rect)

            pygame.display.update()
            self.clock.tick(FRAMERATE)


if __name__ == '__main__':
    game = Game()
    game.run()