"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""

import argparse
from pathlib import Path
from typing import Callable, Dict

from instance import Instance
from solution import Solution
from file_wrappers import StdinFileWrapper, StdoutFileWrapper
from point import Point
import random


def solve_naive(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=instance.cities,
    )

def solve_not_naive(instance: Instance) -> Solution:

    def possible_tower_points(pt, r_s):
        pts = []
        for i in range(max(pt.x - r_s, 0), min(pt.x + r_s, instance.D - 1) + 1):
            for j in range(max(pt.y - r_s, 0), min(pt.y + r_s, instance.D - 1) + 1):
                possible_pt = Point(i, j)
                if possible_pt.distance_sq(pt) <= (r_s ** 2):
                    pts.append(possible_pt)
        return pts

    uncovered_cities = list(instance.cities)
    my_towers = []

    for i in range(instance.D):
        for j in range(instance.D):
            curr_point = Point(i, j)
            if curr_point in uncovered_cities:
                possible_pts = possible_tower_points(curr_point, instance.R_s)
                max_cities_covered = sum([ct.distance_sq(possible_pts[0]) <= (instance.R_s ** 2) for ct in uncovered_cities])
                next_tower = possible_pts[0]
                num_towers_in_p_area = sum([next_tower.distance_sq(tw) <= (instance.R_p ** 2) for tw in my_towers])
                for k in range(1, len(possible_pts)):
                    num_cities_covered = sum([ct.distance_sq(possible_pts[k]) <= (instance.R_s ** 2) for ct in uncovered_cities])
                    if num_cities_covered > max_cities_covered:
                        max_cities_covered = num_cities_covered
                        next_tower = possible_pts[k]
                        num_towers_in_p_area = sum([next_tower.distance_sq(tw) <= (instance.R_p ** 2) for tw in my_towers])
                    elif num_cities_covered == max_cities_covered:
                        curr_num_towers_in_p_area = sum([possible_pts[k].distance_sq(tw) <= (instance.R_p ** 2) for tw in my_towers])
                        if curr_num_towers_in_p_area < num_towers_in_p_area:
                            num_towers_in_p_area = curr_num_towers_in_p_area
                            next_tower = possible_pts[k]
                if next_tower not in my_towers:
                    my_towers.append(next_tower)
                    m = 0
                    while m < len(uncovered_cities):
                        if uncovered_cities[m].distance_sq(next_tower) <= (instance.R_s ** 2):
                            uncovered_cities.pop(m)
                        else:
                            m += 1

    #print(all([any([ct.distance_sq(tw) for tw in my_towers]) for ct in instance.cities]))

    return Solution(
        instance=instance,
        towers=my_towers,
    )


"""
def solve_not_naive_randomized(instance: Instance) -> Solution:

    def possible_tower_points(pt, r_s):
        pts = []
        for i in range(max(pt.x - r_s, 0), min(pt.x + r_s, instance.D - 1) + 1):
            for j in range(max(pt.y - r_s, 0), min(pt.y + r_s, instance.D - 1) + 1):
                possible_pt = Point(i, j)
                if possible_pt.distance_sq(pt) <= (r_s ** 2):
                    pts.append(possible_pt)
        return pts

    curr_solution = None
    smallest_penalty = float('inf')

    for i in range(100):
        uncovered_cities = list(instance.cities)
        my_towers = []
        while len(uncovered_cities) > 0:
            #print(len(uncovered_cities))
            city_to_cover = random.choice(uncovered_cities)
            possible_pts = possible_tower_points(city_to_cover, instance.R_s) # no bug for now
            max_cities_covered = sum([ct.distance_sq(possible_pts[0]) <= (instance.R_s ** 2) for ct in uncovered_cities])
            next_tower = possible_pts[0]
            num_towers_in_p_area = sum([next_tower.distance_sq(tw) <= (instance.R_p ** 2) for tw in my_towers])
            for k in range(1, len(possible_pts)):
                num_cities_covered = sum([ct.distance_sq(possible_pts[k]) <= (instance.R_s ** 2) for ct in uncovered_cities])
                if num_cities_covered > max_cities_covered:
                    max_cities_covered = num_cities_covered
                    next_tower = possible_pts[k]
            #print(uncovered_cities)
            #print(city_to_cover)
            #print(next_tower)
            if next_tower not in my_towers:
                #print(next_tower not in my_towers)
                my_towers.append(next_tower)
                m = 0
                while m < len(uncovered_cities):
                    if uncovered_cities[m].distance_sq(next_tower) <= (instance.R_s ** 2):
                        uncovered_cities.pop(m)
                    else:
                        m += 1
        #print('exited while loop')
        new_solution = Solution(instance = instance, towers = my_towers)
        penalty_of_new_solution = new_solution.penalty()
        if penalty_of_new_solution < smallest_penalty:
            curr_solution = new_solution
            smallest_penalty = penalty_of_new_solution

    return curr_solution """


SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive,
    "clever": solve_not_naive
    #"randomized": solve_not_naive_randomized
}


# You shouldn't need to modify anything below this line.
def infile(args):
    if args.input == "-":
        return StdinFileWrapper()

    return Path(args.input).open("r")


def outfile(args):
    if args.output == "-":
        return StdoutFileWrapper()

    return Path(args.output).open("w")


def main(args):
    with infile(args) as f:
        instance = Instance.parse(f.readlines())
        solver = SOLVERS[args.solver]
        solution = solver(instance)
        assert solution.valid()
        with outfile(args) as g:
            print("# Penalty: ", solution.penalty(), file=g)
            solution.serialize(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a problem instance.")
    parser.add_argument("input", type=str, help="The input instance file to "
                        "read an instance from. Use - for stdin.")
    parser.add_argument("--solver", required=True, type=str,
                        help="The solver type.", choices=SOLVERS.keys())
    parser.add_argument("output", type=str,
                        help="The output file. Use - for stdout.",
                        default="-")
    main(parser.parse_args())
