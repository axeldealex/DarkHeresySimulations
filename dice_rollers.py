####################################
# Dark Heresy 2e hit roller implemented in Python
# Doing this to prove to my GM that the sniper rifle upgrade he's offering me is close to redundant
# Planning to implement more weapon qualities, those are seen in the below TODO
# Might upload this to Github as a weird portfolio piece at some point, I do intend to fully document this thing
# Will see if actually ends up happening
####################################

# TODO
# implement razor sharp
# implement automatic histogram plotting
# implement hit rate
# implement expected damage value
# implement targets with AP and soak

import argparse
import random


def parse_args():
    """
    Parses input from command line to run the script
    """
    parser = argparse.ArgumentParser(prog='python3 dice_rollers.py',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     description='  Rolls dice given certain attributes passed as flags.\n'
                                     '  WIP as of now\n'
                                     '\n'
                                     'defaults:\n'
                                     '  no extra properties on the weapon\n'
                                     '  target = 50\n')
    parser.add_argument('-n', dest='n_rolls', default=1000, type=int,
                        help='number of rolls to simulate')
    parser.add_argument('-t', '--target', dest='target', default=50, type=int,
                        help='target to hit. Must be a positive integer.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='print some of the progress to the terminal', default=False)
    parser.add_argument('-p', '--proven', dest='proven', default=False, type=int,
                        help='proven, minimal value of the damage die. '
                             'Must be a positive integer below 10 and above 1.')
    parser.add_argument('-a', '--accurate', dest='accurate', action='store_true', default=False,
                        help='accurate, adds extra damage die on high DoS. True or False.')
    parser.add_argument('-s', '--sides', dest='sides', default=10, type=int,
                        help='number of sides on a damage die. Needs to be a positive integer above 1.')

    args = parser.parse_args()

    if (args.proven < 2 or args.proven >= args.sides) and args.proven:
        parser.error("invalid number for proven")

    if args.sides < 2:
        parser.error("invalid number for sides")

    if args.n_rolls < 1:
        parser.error("n_rolls must be a positive integer")

    if args.target < 1:
        parser.error("target must be a positive integer")

    return args


def damage_roll(DoS, accurate, proven=False, sides=10):
    """"
    Rolls a single die with specified amount of sides
    proven is the minimum value of a die
    """
    roll = random.randint(1, sides)
    if proven:
        if roll < proven:
            roll = proven

    if accurate:
        if (DoS - 1) // 2 > 1:
            roll = roll + random.randint(1, sides)
        if (DoS - 1) // 2 > 2:
            roll = roll + random.randint(1, sides)
    return roll


def determine_location(hit_roll):
    """"
    Given a hit roll, determines the location of the target hit following Dark Heresy 2 rules
    """
    first_num = hit_roll % 10
    second_num = hit_roll // 10
    reverse_num = first_num * 10 + second_num

    if reverse_num <= 10:
        return "head"
    elif reverse_num <= 20:
        return "arm_right"
    elif reverse_num <= 30:
        return "arm_left"
    elif reverse_num <= 70:
        return "body"
    elif reverse_num <= 85:
        return "leg_left"
    else:
        return "leg_right"


def hit_roller(target, proven, sides, accurate):
    """"
    Determines if the attack hits
    returns a dict with:
        result (True/False)
        degrees (degrees of success if positive,
                negative if failure)
        location (string with location hit)
        hit_roll (int of original roll)
    """
    # rolls the set
    hit_roll = random.randint(1, 100)

    # set values for a success
    if hit_roll <= target:
        result = True
        degrees = target // 10 - hit_roll // 10 + 1
        damage = damage_roll(degrees, accurate, proven, sides)
    # or a fail
    else:
        degrees = target // 10 - hit_roll // 10 - 1
        result = False
        damage = "miss"

    # returns the result of the hit in a dict
    return {"result": result,
            "degrees": degrees,
            "location": determine_location(hit_roll),
            "hit_roll": hit_roll,
            "damage": damage}


def dice_roller(n_dice, target, accurate=False, proven=False, sides=10):
    """"
    Rolls a predefined number of dice with specified amount of sides
    target is the number to beat (lower = success) on a d100
    accurate is
    proven is the minimum value a die takes, is passed as an input to deeper functions
    returns a list of damage die
    """

    # init empty list for storing rolls
    rolls = []
    # rolls the n_dice times
    for i in range(n_dice):
        # and appends to list
        rolls.append(hit_roller(target, proven, sides, accurate))
    return rolls


def main(args=False):
    """
    Runs the script given commands from argparser
    """
    if not args:
        args = parse_args()

    rolls = dice_roller(args.n_rolls, args.target, args.sides)
    print(len(rolls))


if __name__ == '__main__':
    main()
