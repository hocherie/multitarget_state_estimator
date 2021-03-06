__author__ = 'cherieho'
# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2011-11-15
#
# ------------------------------------------------------------------------

import math
import turtle
import random

turtle.tracer(50000, delay=0)
turtle.register_shape("dot", ((-3,-3), (-3,3), (3,3), (3,-3)))
turtle.register_shape("tri", ((-3, -2), (0, 3), (3, -2), (0, 0)))
turtle.speed(0)
turtle.title("Find the robot")

UPDATE_EVERY = 0
DRAW_EVERY = 0

class Maze(object):
    def __init__(self, maze, half_width, half_height):
        self.maze = maze
        self.half_width = half_width
        self.half_height = half_height
        self.width   = half_width * 2.0
        self.height  = half_height * 2.0
        turtle.setworldcoordinates(-self.half_width, -self.half_height, self.half_width, self.half_height)
        self.blocks = []
        self.update_cnt = 0
        self.one_px = float(turtle.window_width()) / float(self.width) / 2

        self.beacons = []
        for y, line in enumerate(self.maze):
            for x, block in enumerate(line):
                if block:
                    nb_y = self.height - y - 1
                    self.blocks.append((x, nb_y))
                    if block == 2:
                        self.beacons.extend(((x, nb_y), (x+1, nb_y), (x, nb_y+1), (x+1, nb_y+1)))

    def draw(self):
        for x, y in self.blocks:
            turtle.up()
            turtle.setposition(x, y)
            turtle.down()
            turtle.setheading(90)
            turtle.begin_fill()
            for _ in range(0, 4):
                turtle.fd(1)
                turtle.right(90)
            turtle.end_fill()
            turtle.up()

        turtle.color("#00ffff")
        for x, y in self.beacons:
            turtle.setposition(x, y)
            turtle.dot()
        turtle.update()

    def weight_to_color(self, weight):
        return "#%02x00%02x" % (int(weight * 255), int((1 - weight) * 255))

    # def is_in(self, x, y):
    #     if x < 0 or y < 0 or x > self.width or y > self.height:
    #         return False
    #     return True

    def is_free(self, x, y):
        return True

    def show_mean(self, mean):
        # TODO: Delete below assumption about confident
        confident = True
        m1, m2 = mean
        x = 0
        y = 0
        if confident:
            turtle.color("#00AA00")
            turtle.fillcolor("")
        else:
            turtle.color("#cccccc")
            turtle.fillcolor("")
        turtle.setposition(x, y)
        turtle.shape("circle")
        turtle.stamp()

    def clearMaze(self):
        turtle.clearstamps()

    def show_particles(self, particles):
        self.update_cnt += 1
        if UPDATE_EVERY > 0 and self.update_cnt % UPDATE_EVERY != 1:
            return

        # turtle.clearstamps()
        turtle.shape('tri')

        draw_cnt = 0
        px = {}
        for p in particles:
            draw_cnt += 1
            if DRAW_EVERY == 0 or draw_cnt % DRAW_EVERY == 1:
                # Keep track of which positions already have something
                # drawn to speed up display rendering
                scaled_x1 = int(p.x1 * self.one_px)
                scaled_y1 = int(p.y1 * self.one_px)
                scaled_xy1 = scaled_x1 * 10000 + scaled_y1
                if not scaled_xy1 in px:
                    px[scaled_xy1] = 1
                    turtle.setposition(*p.xy1)
                    turtle.setheading(math.degrees(p.h))
                    turtle.color("Red")
                    turtle.stamp()

                    turtle.setposition(*p.xy2)
                    turtle.setheading(math.degrees(p.h))
                    turtle.color("Blue")
                    turtle.stamp()
    def show_att_line(self, (x1, y1), (x2, y2)):
        turtle.penup()
        turtle.pensize(5)
        turtle.pencolor("black")
        turtle.goto(x1, y1)
        turtle.pendown()
        turtle.goto(x2, y2)
        turtle.penup()

    def show_est_line(self, (x1, y1), (x2, y2)):
        turtle.clear()
        turtle.penup()
        turtle.pencolor("blue")
        turtle.goto(x1, y1)
        turtle.pendown()
        turtle.goto(x2, y2)
        turtle.penup()


    def show_sharks(self, sharks):
        self.update_cnt += 1
        if UPDATE_EVERY > 0 and self.update_cnt % UPDATE_EVERY != 1:
            return

        turtle.clearstamps()
        draw_cnt = 0
        px = {}
        for shark in sharks:
            draw_cnt += 1
            shark_shape = 'classic' if shark.tracked else 'classic'
            if DRAW_EVERY == 0 or draw_cnt % DRAW_EVERY == 0:
                # Keep track of which positions already have something
                # drawn to speed up display rendering
                scaled_x = int(shark.x * self.one_px)
                scaled_y = int(shark.y * self.one_px)
                scaled_xy = scaled_x * 10000 + scaled_y
                turtle.color(shark.color)
                turtle.shape(shark_shape)
                turtle.resizemode("user")
                turtle.shapesize(1.5,1.5,1)
                if not scaled_xy in px:
                    px[scaled_xy] = 1
                    turtle.setposition(*shark.xy)
                    turtle.setheading(math.degrees(shark.h))
                    turtle.stamp()


    def show_shark(self, shark):
        turtle.color(shark.color)
        turtle.shape('turtle')
        turtle.setposition(*shark.xy)
        turtle.setheading(math.degrees(shark.h))
        turtle.stamp()
        turtle.update()
        # turtle.clearstamps()

    def show_attraction_point(self, att):
        turtle.color('black')
        turtle.shape('circle')
        turtle.fillcolor("")
        turtle.resizemode("user")
        turtle.shapesize(1.5, 1.5, 1)

        turtle.setposition(att)
        turtle.setheading(0)
        turtle.stamp()
        turtle.update()
        # turtle.clearstamps()

    def show_robot(self, robot):
        turtle.color("blue")
        turtle.shape('square')
        turtle.setposition(*robot.xy)
        turtle.setheading(math.degrees(robot.h))
        turtle.stamp()
        turtle.update()

    def random_place(self):
        x = random.uniform(-self.half_width, self.half_width)
        y = random.uniform(-self.half_height, self.half_height)
        return x, y

    def random_free_place(self):
        while True:
            x, y = self.random_place()
            if self.is_free(x, y):
                return x, y

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)