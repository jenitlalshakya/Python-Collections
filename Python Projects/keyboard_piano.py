import pygame

pygame.init()
pygame.mixer.init()

KEY_SOUNDS = {
    pygame.K_a: "C.wav",
    pygame.K_s: "D.wav",
    pygame.K_d: "E.wav",
    pygame.K_f: "F.wav",
    pygame.K_g: "G.wav",
    pygame.K_h: "A.wav",
    pygame.K_j: "B.wav",
    pygame.K_k: "C_high.wav"
}

sounds = {key: pygame.mixer.Sound(file) for key, file in KEY_SOUNDS.items()}

screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption("Python Keyboard Piano")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in sounds:
                sounds[event.key].play()


pygame.quit()