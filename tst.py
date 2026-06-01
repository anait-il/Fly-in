import pygame
pygame.init()

surface = pygame.display.set_mode((800, 600))
running = True
while running:
    for move in pygame.event.get():
        if move.type == pygame.QUIT:
            running = False
        if move.key == pygame.K_q:
            running = False
    pygame.draw.line(surface, 'red', (0,600), (800, 0))
    pygame.display.flip()

