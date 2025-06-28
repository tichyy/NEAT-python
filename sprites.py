import pygame
from settings import *

class Background(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        bg_image = pygame.image.load('assets/background.png')
        scaled_width = bg_image.get_width() * scale_factor
        scaled_height = bg_image.get_height() * scale_factor
        scaled_image = pygame.transform.scale(bg_image, (scaled_width, scaled_height))

        self.image = pygame.Surface((scaled_width*2,scaled_height))
        self.image.blit(scaled_image, (0,0))
        self.image.blit(scaled_image, (scaled_width,0))
        self.rect = self.image.get_rect(topleft = (0,0))
        self.pos = pygame.math.Vector2(self.rect.topleft) # what

    def update(self, dt):
        self.pos.x -= 300 * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0
        self.rect.x = round(self.pos.x)


class Bird(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)

        # image
        # change this !
        img = pygame.image.load('assets/bird.png').convert_alpha()
        self.image = pygame.transform.scale(img, pygame.math.Vector2(img.get_size()) * scale_factor * 0.9)
        # change this !
        self.base_image = self.image

        # rect
        self.rect = self.image.get_rect(midleft = (SCREEN_WIDTH/10,SCREEN_HEIGHT/2))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # movement
        self.gravity = 800
        self.direction = 0

        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def apply_gravity(self, dt):
        self.direction += self.gravity * dt
        self.pos.y += self.direction * dt
        self.rect.y = round(self.pos.y)

    def rotate(self):
        rotated_bird = pygame.transform.rotozoom(self.base_image, -self.direction * 0.08, 1)
        self.image = rotated_bird
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.apply_gravity(dt)
        self.rotate()

    def jump(self):
        self.direction = - 400


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor, orientation, x, yr, gap):
        super().__init__(groups)
        surf = pygame.image.load('assets/obstacle.png').convert_alpha()
        self.image  = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)

        if orientation == 'bottom':
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midbottom=(x, SCREEN_HEIGHT + yr))
        else:
            self.rect = self.image.get_rect(midtop=(x,-(gap-yr)))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.pos.x -= 300 * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -100:
            self.kill()
