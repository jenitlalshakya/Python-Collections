import pygame
import math
import random

def pong_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    left_paddle = pygame.Rect(50, 250, 20, 100)
    right_paddle = pygame.Rect(730, 250, 20, 100)
    paddle_speed = 8

    ball = pygame.Rect(390, 290, 20, 20)
    ball_speed = [0, 0]
    base_speed = 5

    score = [0, 0]
    font = pygame.font.Font(None, 36)

    def reset_ball():
        ball.center = (400, 300)
        angle = random.uniform(-math.pi/4, math.pi/4)
        direction = random.choice([-1, 1])
        ball_speed[0] = direction * base_speed + math.cos(angle)
        ball_speed[1] = base_speed * math.sin(angle)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= paddle_speed
        if keys[pygame.K_s] and left_paddle.bottom < 600:
            left_paddle.y += paddle_speed
        if keys[pygame.K_UP] and right_paddle.top > 0:
            right_paddle.y -= paddle_speed
        if keys[pygame.K_DOWN] and right_paddle.bottom < 600:
            right_paddle.y += paddle_speed

        if ball_speed == [0, 0]:
            reset_ball()

        ball.x += ball_speed[0]
        ball.y += ball_speed[1]

        if ball.top <= 0 or ball.bottom >= 600:
            ball_speed[1] = -ball_speed[1]

        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            ball_speed[0] = -ball_speed[0] * 1.1
            ball_speed[1] *= 1.1

        if ball.left <= 0:
            score[1] += 1
            reset_ball()
        if ball.right >= 800:
            score[0] += 1
            reset_ball()

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (0, 255, 0), left_paddle)
        pygame.draw.rect(screen, (0, 255, 0), right_paddle)
        pygame.draw.ellipse(screen, (255, 0, 0), ball)
        score_text = font.render(f"{score[0]} - {score[1]}",
                                    True, (255, 255, 255))
        screen.blit(score_text, (380, 10))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    pong_game()
