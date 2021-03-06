from __future__ import absolute_import

import numpy as np
import matplotlib.pyplot as plt
import shark_particle as sp
import bisect
import random
from shapely.geometry import LineString, Point
import math
import scipy.stats

TIME_STEPS = 1000
# SIGMA_MEAN = 0.1
SHOW_VISUALIZATION = False  # Whether to have visualization
PARTICLE_COUNT = 50
TRACK_COUNT = 1
ROBOT_HAS_COMPASS = False


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
def gauss(error, sd):
    # TODO: variance is derived experimentally
    return scipy.stats.norm.pdf(error, 0, sd)
def moving_average(data, number_points):
    """ Computes the moving average of data using number_points of last data.
    """
    length = len(data)
    if length < number_points:
        return sum(data) / float(length)
    else:
        return sum(data[length - number_points:]) / float(number_points)


def compute_shark_mean(sharks, track_number):
    """ Computes the mean position of the tracked sharks
    tracked_sharks: List of tracked sharks
    """
    m_x, m_y = 0, 0

    for shark in sharks[:track_number]:
        m_x += shark.x
        m_y += shark.y

    x_mean = m_x / track_number
    y_mean = m_y / track_number

    return x_mean, y_mean

def distance_from_line(shark, line):
    p = Point(shark.x, shark.y)
    return p.distance(line)

def total_shark_distance_from_line(sharks, line):
    total = 0
    for shark in sharks:
        # Trying least squares
        total += distance_from_line(shark, line)
    return total

def compute_particle_means(particles, world):
    """
    Compute the mean for all particles that have a reasonably good weight.
    This is not part of the particle filter algorithm but rather an
    addition to show the "best belief" for current position.
    """
    m_x1, m_y1, m_x2, m_y2, m_count, m_num_sharks = 0, 0, 0, 0, 0, 0
    for p in particles:
        m_count += p.w
        m_x1 += p.x1 * p.w
        m_y1 += p.y1 * p.w
        m_x2 += p.x2 * p.w
        m_y2 += p.y2 * p.w
        m_num_sharks += p.num_sharks * p.w

    if m_count == 0:
        return (0,0), (0,0)

    m_x1 /= m_count
    m_y1 /= m_count
    m_x2 /= m_count
    m_y2 /= m_count
    m_num_sharks /= m_count

    # Now compute how good that mean is -- check how many particles
    # actually are in the immediate vicinity
    m_count = 0
    for p in particles:
        if world.distance(p.x1, p.y1, m_x1, m_y1) < 1:
            m_count += 1

    return (m_x1, m_y1), (m_x2, m_y2), m_num_sharks


def estimate(particles, world, sharks):

    # Update particle weight according to how good every particle matches

    for j, p in enumerate(particles):
        particle_line = LineString([(p.x1, p.y1), (p.x2, p.y2)])
        particle_error = total_shark_distance_from_line(sharks, particle_line)
        weight_particle = gauss(particle_error, get_sd_from_num_sharks(p.num_sharks))
        p.w = weight_particle

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
            new_particle = sp.Particle.create_random(1, world)[0]
        else:
            new_particle = sp.Particle(p.x1, p.y1, p.x2, p.y2, p.num_sharks,
                                       heading=robot1.h if ROBOT_HAS_COMPASS else p.h,
                                       noisy=True)
        new_particles.append(new_particle)
    return new_particles

def get_sd_from_num_sharks(num_sharks):
    """Get sd for PF. sd from Gaussian Fit.
    sd = 1.551*num_sharks - 15.7406"""
    return 1.551 * num_sharks - 15.7406

def errorIndividualPlot(error_x, error_y):
    """ Save error_x and error_y plot to current folder.

    :param error_x: Error in x direction
    :param error_y: Error in y direction
    :return: Shows error plots
    """
    fig, axes = plt.subplots(nrows=2, ncols=1)

    axes[0].plot(error_x)
    axes[0].set_ylabel('Error in x')
    axes[0].set_title(
        'No. of Particles : %s, Tracked Sharks: %s of %s' % (PARTICLE_COUNT, TRACK_COUNT, sp.SHARK_COUNT))
    axes[0].set_ylim([-2, 2])
    axes[1].plot(error_y)
    axes[1].set_ylabel('Error in y')
    axes[1].set_ylim([-2, 2])

    plt.savefig('MeanPointPF%sParticles%s of %sTrackedSharks.png' % (PARTICLE_COUNT, TRACK_COUNT, sp.SHARK_COUNT))
    plt.close()

def errorPlot(error_x, error_y, track_count):
        """ Plot error_x and error_y

        :param error_x: Error in x direction
        :param error_y: Error in y direction
        :return: Plots error
        """
        axes[0].plot(error_x, label=track_count)
        axes[1].plot(error_y, label=track_count)



def run(shark_count, track_count, my_file, attraction_line):
    """ Run particle filter with shark_count of sharks with track_count tracked.
    """
    world = sp.Maze(sp.maze_data, sp.HALF_WIDTH, sp.HALF_HEIGHT)

    if SHOW_VISUALIZATION:
        world.draw()

    # Initialize Items
    sharks = sp.Shark.create_random(shark_count, world, track_count)
    robots = sp.Robot.create_random(0, world)

    # Allow sharks to reach attraction line first
    particles_list = []
    for time_step in range(300):
        sp.move(world, robots, sharks, attraction_line, particles_list, sp.SIGMA_RAND, sp.K_ATT, sp.K_REP)

    # Start PF
    particles_list = [sp.Particle.create_random(PARTICLE_COUNT, world)]

    # Initialize error lists
    error_list = []
    est_numSharks = []



    for time_step in range(TIME_STEPS):

        # Calculate mean position
        p_means_list = []

        for i, particles in enumerate(particles_list):
            particles_list[i] = estimate(particles, world, sharks)

        m1, m2, m_num_sharks = compute_particle_means(particles, world)
        #TODO
        p_means_list.append(m1)

        # # ---------- Move things ----------
        # Move sharks with shark's speed
        sp.move(world, robots, sharks, attraction_line, particles_list, sp.SIGMA_RAND, sp.K_ATT, sp.K_REP)
        #TODO: Let p_means be shark mean for now

        # Find total error (performance metric) and add to list
        est_line = LineString([m1, m2])

        est_error_sum = 0
        act_error_sum = 0
        raw_error_sum = 0

        for shark in sharks:
            raw_error_sum += distance_from_line(shark, est_line) - distance_from_line(shark, attraction_line)

        error = math.sqrt(raw_error_sum)

        error_list.append(error)
        est_numSharks.append(m_num_sharks)

        # Show current state
        if SHOW_VISUALIZATION:
            sp.show(world, robots, sharks, particles_list, p_means_list, m1, m2, attraction_line)

        print time_step, "est_num_sharks: ", m_num_sharks


    for item in error_list:
        my_file.write(str(item) + ",")
    my_file.write("\n")

    for item in est_numSharks:
        my_file2.write(str(item) + ",")
    my_file.write("\n")

def generate_random_point():
    x_rand = random.random() * sp.WIDTH - sp.HALF_WIDTH
    y_rand = random.random() * sp.HEIGHT - sp.HALF_HEIGHT
    return (x_rand, y_rand)

def main():

    for shark_count in range(101)[30::10]:
        # shark_count = 50
        num_trials = 5

        # Export shark mean position over time into text file, can be plotted with matlab
        act_line_start = (-sp.HALF_WIDTH, -0.2168 * -sp.HALF_WIDTH + 0.113)
        act_line_end = (sp.HALF_WIDTH, -0.2168 * sp.HALF_WIDTH + 0.113)
        attraction_line = LineString([act_line_start, act_line_end])

        global my_file
        my_file = open("att_line_pf_%sSharks.txt" %(shark_count), "w")
        my_file.write("Line Start: %s, Line End: %s" %(act_line_start, act_line_end))
        my_file.write("\n")
        my_file.write("NumSharks: %s, K_att: %s, K_rep: %s, Sigma_Rand: %s, Speed/ts: %s"
                      %(shark_count, sp.K_ATT, sp.K_REP, sp.SIGMA_RAND, sp.Shark.speed))
        my_file.write("\n")
        my_file.write("x, y for all sharks, line break represents next time step")
        my_file.write("\n")

        global my_file2
        my_file2 = open("att_numsharks_%sSharks.txt" % (shark_count), "w")

        for _ in range(num_trials):
            run(shark_count, shark_count, my_file, attraction_line)

        my_file.close()
        my_file2.close()


if __name__ == "__main__":
    main()
