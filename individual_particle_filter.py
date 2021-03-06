# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2011-11-15
#  Modified by Cherie Ho on 2015-11-11
#
# ------------------------------------------------------------------------

from __future__ import absolute_import

import random
import math
import bisect
import scipy.stats
import matplotlib.pyplot as plt
from draw import Maze
import shark_particle as sp
import numpy as np

# 0 - empty square
# 1 - occupied square
# 2 - occupied square with a beacon at each corner, detectable by the robot

# Smaller maze

MAZE_DATA = ((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ),
             ( 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))


# Constants

PARTICLE_COUNT = 50   # Total number of particles
TIME_STEPS = 1000 # Number of steps before simulation ends
SHARK_COUNT = 50 # Number of sharks
ROBOT_COUNT = 2 # Number of robots
TRACK_COUNT = 0 # Number of tracked sharks

SHOW_VISUALIZATION = True # Whether to have visualization

ROBOT_HAS_COMPASS = False
# ------------------------------------------------------------------------
# Some utility functions

def add_noise(level, *coords):
    return [x + random.uniform(-level, level) for x in coords]

def add_little_noise(*coords):
    return add_noise(0.02, *coords)

def add_some_noise(*coords):
    return add_noise(0.1, *coords)

def gauss(error):
    # TODO: variance is derived experimentally
    return scipy.stats.norm.pdf(error, 0, 0.1)

# ------------------------------------------------------------------------
def compute_particle_mean(particles, world):
    """
    Compute the mean for all particles that have a reasonably good weight.
    This is not part of the particle filter algorithm but rather an
    addition to show the "best belief" for current position.
    """
    m_x, m_y, m_count = 0, 0, 0
    for p in particles:
        m_count += p.w
        m_x += p.x * p.w
        m_y += p.y * p.w

    if m_count == 0:
        return -1, -1, False

    m_x /= m_count
    m_y /= m_count

    # Now compute how good that mean is -- check how many particles
    # actually are in the immediate vicinity
    m_count = 0
    for p in particles:
        if world.distance(p.x, p.y, m_x, m_y) < 1:
            m_count += 1

    return m_x, m_y, m_count > PARTICLE_COUNT * 0.95

# ------------------------------------------------------------------------
class WeightedDistribution(object):
    def __init__(self, state):
        accum = 0.0
        self.state = [p for p in state if p.w > 0]
        self.distribution = []
        for x in self.state:
            accum += x.w
            self.distribution.append(accum)

    def pick(self):
        try:
            # TODO: ask Chris about how to pick
            # Pick randomly from self.distribution
            return self.state[bisect.bisect_left(self.distribution, random.uniform(0, 1))]
        except IndexError:
            # Happens when all particles are improbable w=0
            return None

# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
class Robot(Particle):
    speed = 1

    def __init__(self, x, y, heading=None, w=1, noisy=False):
        if heading is None:
            heading = random.uniform(0, math.pi)
        if noisy:
            x, y, heading = add_some_noise(x, y, heading)

        self.x = 8
        self.y = 8
        self.h = heading
        self.w = w
        self.step_count = 0
        # self.color = random.random(), random.random(), random.random()


    def chose_random_direction(self):
        heading = random.uniform(0, math.pi)
        self.h = heading

    def move(self, maze):
        """
        Move the robot. Note that the movement is stochastic too.
        """
        while True:
            self.step_count += 1
            if self.advance_by(self.speed, noisy=True,
                checker=lambda r, dx, dy: maze.is_free(r.x+dx, r.y+dy)):
                break
            # Bumped into something or too long in same direction,
            # chose random new direction
            self.chose_random_direction()



# ------------------------------------------------------------------------

class Shark(Particle):
    speed = 0.05

    def __init__(self, x, y, tracked=False, heading=None, w=1, noisy=False):
        if heading is None:
            heading = random.uniform(- math.pi, math.pi)
        if noisy:
            x, y, heading = add_some_noise(x, y, heading)

        self.x = 0
        self.y = 0
        self.h = heading
        self.tracked = tracked
        self.w = w
        self.step_count = 0
        self.color = random.random(), random.random(), random.random()
        self.in_zone = False
        self.last_alpha = 0

    def __repr__(self):
        return "(%f, %f, w=%f, tracked=%r)" % (self.x, self.y, self.w, self.tracked)
    @classmethod
    def create_random(cls, count, maze, track_count):
        return [cls(*maze.random_free_place(), tracked=True if i<track_count else False) for i in range(0, count)]

    def chose_random_direction(self):
        heading = random.uniform(0, math.pi)
        self.h = heading

    def distance(self, shark):
        return math.sqrt((self.x - shark.x) ** 2 + (self.y - shark.y) ** 2)

    def read_distance_sensor(self, robot):
        """
        Poor robot, it's sensors are noisy and pretty strange,
        it can only know laser sensor wall distance(!)
        and is not very accurate at that too!
        """
        return add_little_noise(super(Shark, self).read_distance_sensor(robot))[0]

    def move(self, maze):
        """
        Move the robot. Note that the movement is stochastic too.
        """
        while True:
            self.step_count += 1
            if self.advance_by(self.speed, noisy=True,
                checker=lambda r, dx, dy: maze.is_free(r.x+dx, r.y+dy)):
                break
            # Bumped into something or too long in same direction,
            # chose random new direction
            self.chose_random_direction()

    def angle_diff(self, desired_theta):
        """
        :return: Difference between heading and desired_theta within -pi and pi.
        """
        h = self.h
        a = desired_theta - h
        while a > math.pi:
            a -= 2 * math.pi
        while a < -math.pi:
            a += 2 * math.pi
        return a

    def find_repulsion(self, sharks):
        """
        :param sharks: list of sharks
        :return: Repulsion contribution (x and y) to movement
        """
        x_rep = 0
        y_rep = 0
        for shark in sharks:
            dist = self.distance(shark)
            if dist < sp.FISH_INTERACTION_RADIUS and dist != 0:
                mag = (1 / dist - 1 / sp.FISH_INTERACTION_RADIUS) ** 2
                x_rep += mag * (self.x - shark.x)
                y_rep += mag * (self.y - shark.y)
        return x_rep, y_rep

    def find_attraction(self, attractors):
        """
        :param attractors: List of attraction points
        :return: Attractor contribution (x and y) to shark's movement
        """
        x_att = 0
        y_att = 0
        for attractor in attractors:
            mag = (attractor[0] - self.x) ** 2 + (attractor[1] - self.y) ** 2
            x_att += mag * (attractor[0] - self.x)
            y_att += mag * (attractor[1] - self.y)
        return x_att, y_att

    def advance(self, sharks, speed, sigma_rand, k_att, k_rep, noisy=False, checker=None):
        """
        :param
                k_att: Attraction Gain
                k_rep: Repulsive Gain
        :return: Advance shark by one step.
        """
        # Get attributes
        x_att, y_att = self.find_attraction(sp.ATTRACTORS)
        x_rep, y_rep = self.find_repulsion(sharks)

        # Sum all potentials
        x_tot = k_att * x_att + k_rep * x_rep
        y_tot = k_att * y_att + k_rep * y_rep
        desired_theta = math.atan2(y_tot, x_tot)

        # Set yaw control
        control_theta = sp.K_CON * (self.angle_diff(desired_theta)) + sigma_rand * np.random.randn(1)[0]
        control_theta = min(max(control_theta, - sp.MAX_CONTROL), sp.MAX_CONTROL)
        self.h += control_theta

        # Calculate cartesian distance
        dx = math.cos(self.h) * speed
        dy = math.sin(self.h) * speed

        # Checks if, after advancing, shark is still in the box
        if checker is None or checker(self, dx, dy):
            self.move_by(dx, dy)
            return True
        return False


def estimate(robots, shark, particles, world, error_x, error_y):

    # Initialize lists
    weight_list = [1]*len(particles)

    # Read sensors

    for i, robot in enumerate(robots):
        shark_robot_dist = shark.read_distance_sensor(robot)
        shark_robot_angle = shark.read_angle_sensor(robot)


        # Update particle weight according to how good every particle matches
        # robbie's sensor reading
        for j, p in enumerate(particles):

            particle_robot_dist = p.read_distance_sensor(robot)
            particle_robot_angle = p.read_angle_sensor(robot)


            # Calculate weight from gaussian
            error_dist_particle_robot = shark_robot_dist - particle_robot_dist
            error_angle_particle_robot = shark_robot_angle - particle_robot_angle

            weight_particle_robot = gauss(error_dist_particle_robot) * gauss(error_angle_particle_robot)

            weight_list[j] *= weight_particle_robot

    for i, p in enumerate(particles):

        p.w = weight_list[i]

    # Find the mean point and associated confidence
    m_x, m_y, m_confident = compute_particle_mean(particles, world)

    # Append difference between current and estimated state to lists
    error_x.append(m_x - shark.x)
    error_y.append(m_y - shark.y)


    # Shuffle particles
    new_particles = []

    # Normalise weights
    nu = sum(p.w for p in particles)
    if nu:
        for p in particles:
            p.w = p.w / nu

    # create a weighted distribution, for fast picking
    dist = WeightedDistribution(particles)

    for _ in particles:
        p = dist.pick()
        if p is None:  # No pick b/c all totally improbable
            new_particle = Particle.create_random(1, world)[0]
        else:
            new_particle = Particle(p.x, p.y,
                    heading=robot1.h if ROBOT_HAS_COMPASS else p.h,
                    noisy=True)
        new_particles.append(new_particle)
    return new_particles

def move(world, robots, sharks, particles_list, sigma_rand, k_att, k_rep):
    # ---------- Move things ----------
    for robot in robots:
        robot.move(world)

    d_h = []
    for shark in sharks:
        old_heading = shark.h
        shark.advance(sharks, shark.speed, sigma_rand, k_att, k_rep)
        d_h.append(shark.h - old_heading)


    # Move particles according to my belief of movement (this may
    # be different than the real movement, but it's all I got)
    for i, particles in enumerate(particles_list):

        for p in particles:
            # TODO: find a better way to disperse this (currently: 5 degree)
            p.h += random.uniform(d_h[i], 0.1)  # in case robot changed heading, swirl particle heading too
            p.advance_by(sharks[i].speed)


def errorPlot(error_x, error_y):
    """

    :param error_x: Error in x direction
    :param error_y: Error in y direction
    :return: Shows error plots
    """
    fig, axes = plt.subplots(nrows=2, ncols=1)

    axes[0].plot(error_x)
    axes[0].set_ylabel('Error in x')
    axes[0].set_title('No. of Particles : ' + str(PARTICLE_COUNT))
    axes[1].plot(error_y)
    axes[1].set_ylabel('Error in y')

    plt.show()

def show(world, robots, sharks, particles_list, means_list, attraction_point=(sp.X_ATT, sp.Y_ATT)):
    """
    :param has_particle:
    :return: Shows robots, sharks, particles and means.
    """


    # world.show_particles(particles2)
    for particles in particles_list:
        world.show_particles(particles)
    world.show_attraction_point(attraction_point)



    for mean in means_list:
        world.show_mean(mean)

    for robot in robots:
        world.show_robot(robot)

    world.show_sharks(sharks)

def angle_diff(h, desired_theta):
        """
        :return: Difference between heading and desired_theta within -pi and pi.
        """
        a = desired_theta - h
        while a > math.pi or a < -math.pi:
            if a > math.pi:
                a -= 2 * math.pi
            if a < -math.pi:
                a += 2 * math.pi
        return a
# ------------------------------------------------------------------------

def main():
    world = Maze(MAZE_DATA)

    if SHOW_VISUALIZATION:
        world.draw()

    # Initialize particles, robots, means and sharks
    particles_list = []
    for _ in range(TRACK_COUNT):
        particles_list.append(Particle.create_random(PARTICLE_COUNT, world))
    robots = Robot.create_random(ROBOT_COUNT, world)
    sharks = Shark.create_random(SHARK_COUNT, world, TRACK_COUNT)


    # Initialize error lists
    error_x1 = []
    error_y1 = []

    # Filter for time step
    for time_step in range(TIME_STEPS):

        means_list = []
        for i, particles in enumerate(particles_list):
            particles_list[i] = estimate(robots, sharks[i], particles, world, error_x1, error_y1)
            means_list.append(compute_particle_mean(particles, world))


        # Move robots, sharks and particles
        move(world, robots, sharks, particles_list, sp.SIGMA_RAND, sp.K_ATT, sp.K_REP)


        # Show current state
        if SHOW_VISUALIZATION:
            show(world, robots, sharks, particles_list, means_list)

        print(time_step)


    # Plot actual vs. estimated into graph
    errorPlot(error_x1, error_y1)



if __name__ == "__main__":
    main()
