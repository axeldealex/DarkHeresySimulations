####################################
# Dark Heresy 2e hit roller implemented in Python
# Doing this to prove to my GM that the sniper rifle upgrade he's offering me is close to redundant
# Planning to implement more weapon qualities, those are seen in the below TODO
# Might upload this to Github as a weird portfolio piece at some point, I do intend to fully document this thing
# Will see if that actually ends up happening
####################################

# TODO
# implement razor sharp
# implement graviton
# implement automatic histogram plotting
# implement hit rate
# implement expected damage value per turn
# implement targets with AP and soak
# implement single shot/multi round burst

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
                                     '  target = 50\n'
                                     '  sides = 10\n')

    # parser argument for number of rolls to simulate
    parser.add_argument('-n', dest='n_rolls', default=1000, type=int,
                        help='number of rolls to simulate')
    # parser argument for target to hit
    parser.add_argument('-t', '--target', dest='target', default=50, type=int,
                        help='target to hit. Must be a positive integer.')
    # parser argument for verbose printing
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                        help='print some of the progress to the terminal')

    # flags for weapon traits
    parser.add_argument('-pr', '--proven', dest='proven', default=False, type=int,
                        help='proven, minimal value of the damage die. '
                             'Must be a positive integer below 10 and above 1.')
    parser.add_argument('-a', '--accurate', dest='accurate', action='store_true', default=False,
                        help='accurate, adds extra damage die on high DoS. True or False.')
    parser.add_argument('-b', '--bonus', dest='bonus', default=0, type=int,
                        help='flat bonus to damage')
    parser.add_argument('-g', '-graviton', dest='graviton', default=False, action='store_true',
                        help='graviton, adds extra damage based on the armour of the target')
    parser.add_argument('-p', '--penetration', dest='penetration', default=0, type=int,
                        help='penetration of the weapon, only works against armour on the enemy')

    # selection of which enemy is being shot at
    parser.add_argument('-e', '--enemy', dest='enemy', default='ganger',
                        choices=['tank', 'astartes', 'ganger', 'hiver'],
                        help='selection of which enemy is being shot at - only has limited options')
    # selection of which direction a vehicle is being shot from - only comes into play when tank is chosen.
    parser.add_argument('-f', '--facing', dest='facing', default=False,
                        choices=[False, 'front', 'side', 'rear'],
                        help='selection of which side of a vehicle is being shot at')

    # special flag for changing number of sides - never required for DH2e calculations (except for knives)
    parser.add_argument('-s', '--sides', dest='sides', default=10, type=int,
                        help='number of sides on a damage die. Needs to be a positive integer above 1.')

    args = parser.parse_args()

    # catching errors prematurely
    if (args.proven < 2 or args.proven >= args.sides) and args.proven:
        parser.error("invalid number for proven")
    if args.sides < 2:
        parser.error("invalid number for sides")
    if args.n_rolls < 1:
        parser.error("n_rolls must be a positive integer")
    if args.target < 1:
        parser.error("target must be a positive integer")
    if args.penetration < 0:
        parser.error("penetration must be a positive number")

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


def hit_roller(target, proven, sides, accurate, bonus, vehicle_facing):
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
    if hit_roll >= target:
        result = True
        degrees = target // 10 - hit_roll // 10 + 1
        damage = damage_roll(degrees, accurate, proven, sides) + bonus
    # or a fail
    else:
        degrees = target // 10 - hit_roll // 10 - 1
        result = False
        damage = "miss"

    if not vehicle_facing:
        location = determine_location(hit_roll)
    else:
        location = vehicle_facing

    # returns the result of the hit in a dict
    return {"result": result,
            "degrees": degrees,
            "location": location,
            "hit_roll": hit_roll,
            "damage": damage}


def dice_roller(n_dice, target, damage_bonus, penetration, vehicle_facing, accurate=False, proven=False, sides=10):
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
        rolls.append(hit_roller(target=target, proven=proven, sides=sides, accurate=accurate,
                                bonus=damage_bonus, vehicle_facing=vehicle_facing))
        rolls[i]["penetration"] = penetration
    return rolls


# TODO make this function work by loading in an enemy from a file somewhere before
def get_damage_dealt(hit_roll, enemy, graviton=False):
    """"
    Calculates the exact damage dealt based on enemy armour values, original hit roll and some armour features.
    """

    return 0


def load_enemy(enemy_name):
    """"
    Loads enemy stats from a .txt file, in a pre-made location within the directory
    """
    enemy_fp = "enemies/" + enemy_name + ".txt"
    enemy_stats = {}

    with open(enemy_fp, "r") as f:
        for line in f:
            if line.startswith('#'):
                pass
            else:
                split_line = line.strip("\n").split()
                print(split_line)
                enemy_stats[split_line[0]] = int(split_line[1])

    return enemy_stats


def main(args=False):
    """
    Runs the script given commands from argparser
    """
    if not args:
        args = parse_args()

    enemy_stats = load_enemy(args.enemy)

    rolls = dice_roller(n_dice=args.n_rolls, target=args.target, sides=args.sides,
                        proven=args.proven, accurate=args.accurate, damage_bonus=args.bonus,
                        penetration=args.penetration, vehicle_facing=args.facing)

    hit_rate = 0
    damage_dealt = 0
    for i in range(args.n_rolls):
        if bool(rolls[i]["result"]):
            hit_rate = hit_rate + 1
            damage_dealt = damage_dealt + get_damage_dealt(hit_roll=rolls[i], enemy=enemy_stats,
                                                           graviton=args.graviton)

    hit_rate = hit_rate / args.n_rolls * 100
    average_damage = damage_dealt / args.n_rolls

    # TODO add verbose printing options
    if args.verbose:
        print(f"hit rate was {hit_rate}%")
        pass


if __name__ == '__main__':
    main()

# welcome to the bottom of the file, thanks for checking out the code. Hope its comprehensive enough to understand.
# if you've got any suggestions or want to talk Python DM me on Discord - AxeldeAlex#9520
