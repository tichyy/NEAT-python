import os

import pygame, sys, time, neat
from sprites import Background, Bird, Obstacle
from random import randint
from settings import *

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

        self.pipes = [] # temporary fix
        self.dead_idx = []

        # NEAT
        self.birds = []
        self.nets = []
        self.ge = []

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
            for pipe in self.collision_sprites: # 1 score point for each pipe passed (top + bottom)
                if pipe.info == pipe.rect.bottom:
                    continue
                for bird in self.birds:
                    if pipe.pos.x < bird.pos.x and not pipe.passed:
                        self.score += 1
                        pipe.passed = True
                        for g in self.ge:
                            g.fitness += 5
                        break

            y =  SCREEN_HEIGHT / 15
        else:
            y = SCREEN_HEIGHT / 2 + (self.menu_rect.height / 2)

        score_surf = self.score_font.render(str(self.score), False, (255, 255, 255))
        score_rect = score_surf.get_rect(midtop = (SCREEN_WIDTH / 2, y))
        self.screen.blit(score_surf,score_rect)

    def collision(self, bird):
        if pygame.sprite.spritecollide(bird, self.collision_sprites, False, pygame.sprite.collide_mask):
            return True
        if bird.rect.centery <= 0:
            return True
        if bird.rect.bottom >= SCREEN_HEIGHT:
            return True
        return False

    def run(self, genomes, config): # our fitness function
        self.active = True
        self.score = 0
        for e in self.collision_sprites:
            e.kill()
        self.birds = []
        self.ge = []
        self.nets = []
        self.pipes = []


        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            self.nets.append(net)
            self.birds.append(Bird(self.all_sprites, self.scale_factor * 0.4))
            g.fitness = 0
            self.ge.append(g)

        last_time = time.time()
        while True:
            # delta time
            dt = time.time() - last_time
            last_time = time.time()

            next_pipe = None
            next_pipe_bottom = None
            if len(self.pipes) > 0:
                for bird in self.birds:
                    for pipe in self.pipes:
                        if pipe.rect.right > bird.rect.left:
                            if pipe.info == pipe.rect.bottom:
                                next_pipe_bottom = pipe
                            else:
                                next_pipe = pipe
                            break

            if len(self.birds) == 0:
                break

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == self.obstacle_timer and self.active:
                    x = SCREEN_WIDTH + randint(40, 100)
                    yr = randint(50, 250)
                    if self.score in (20, 50, 100): # maybe should be removed
                        self.gap_size -= 10
                    self.pipes.append(Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 5, 'top', x, yr, self.gap_size))
                    self.pipes.append(Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 5, 'bottom', x, yr, self.gap_size))

            # game logic
            self.screen.fill((0, 0, 0))
            self.all_sprites.update(dt)
            self.pipes = [e for e in self.collision_sprites] # improve soon
            self.all_sprites.draw(self.screen)
            self.display_score()

            if self.active:
                for x, bird in enumerate(self.birds):
                    if self.collision(bird):
                        self.ge[x].fitness -= 1
                        self.birds[x].kill()
                        self.birds.pop(x)
                        self.nets.pop(x)
                        self.ge.pop(x)
                    else:
                        self.ge[x].fitness += 0.1
                        if next_pipe and next_pipe_bottom:
                            pipe1_y = next_pipe.info
                            pipe2_y = next_pipe_bottom.info
                        else:
                            pipe1_y = SCREEN_HEIGHT / 2
                            pipe2_y = SCREEN_HEIGHT / 2
                        output = self.nets[x].activate([
                            abs(bird.pos.y - pipe1_y),
                            abs(bird.pos.y - pipe2_y)
                        ])
                        if output[0] > 0.5:
                            bird.jump()

            else:
                self.screen.blit(self.menu_surf, self.menu_rect)
                self.screen.blit(self.menu_text_surf, self.menu_text_rect)

            pygame.display.update()
            self.clock.tick(FRAMERATE)

def run_neat(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    game = Game()
    winner = p.run(game.run,100)


if __name__ == '__main__':
    # game = Game()
    # game.run()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_feedforward.txt')
    run_neat(config_path)