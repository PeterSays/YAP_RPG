import pygame
from pygame.locals import *

pygame.init()
fps = 60
fps_clock = pygame.time.Clock()
width = 640
height = 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("YAPSRPG")
display_list = []
battling = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # Update game state

    # Display
    for displayed in display_list:
        screen.blit(displayed.sprite, (displayed.x, displayed.y))

    pygame.display.flip()

    fps_clock.tick(fps)

pygame.quit()
