from turtle import *
import math

def cube_3d():
    bgcolor('black')
    tracer(0)
    pensize(3)

    verts = [[-100, -100, -100], [100, -100, -100],
            [100, 100, -100], [-100, 100, -100],
            [-100, -100, 100], [100, -100, 100],
            [100, 100, 100], [-100, 100, 100]]
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6),
            (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

    angle_x = angle_y = 0
    distance = 500

    def project(p):
        factor = distance / (distance + p[2])
        return [p[0] * factor, p[1] * factor]

    def draw():
        nonlocal angle_x, angle_y   # Use global if variable is not associated with any function
        clear()
        rotated = []
        for v in verts:
            rad_x, rad_y = math.radians(angle_x), math.radians(angle_y)
            y = v[1] * math.cos(rad_x) - v[2] * math.sin(rad_x)
            z = v[1] * math.sin(rad_x) + v[2] * math.cos(rad_x)

            x = v[0] * math.cos(rad_y) + z * math.sin(rad_y)
            z = -v[0] * math.sin(rad_y) + z * math.cos(rad_y)
            rotated.append([x, y, z])

        proj = [project(v) for v in rotated]

        for (i, j) in edges:
            pencolor('cyan')
            penup()
            goto(proj[i])
            pendown()
            goto(proj[j])

        angle_x += 1
        angle_y += 0.7
        update()
        ontimer(draw, 20)

    draw()
    done()

if __name__ == '__main__':
    cube_3d()