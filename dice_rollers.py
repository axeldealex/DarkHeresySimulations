####################################
# Dark Heresy 2e hit roller implemented in Python
# Doing this to prove to my GM that the sniper rifle upgrade he's offering me is close to redundant
# Planning to implement more weapon qualities, those are seen in the below TODO
# Might upload this to Github as a weird portfolio piece at some point, I do intend to fully document this thing
# Will see if that actually ends up happening
####################################

# TODO IMPORTANT/KNOWN BUGS

# TODO
# razor sharp implement
# automatic histogram plotting
# more targets
# more weapons
# implement single shot/multi round burst


from loading_funcs import load_enemy, load_weapon
from checker_funcs import check_jam, input_checks
from plotting_funcs import plot_hist, save_hist
from matplotlib import pyplot as plt
from random import randint
from json import dumps
from os import listdir
import argparse


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

    # parser argument to import a weapon preset
    parser.add_argument('-w', '--weapon', dest='weapon', choices=listdir('weapon_presets'), default=False,
                        help='weapon preset to perform calculations with. Takes precedence over manual values.')

    parser.add_argument('-o', '--output', dest='output', default="False",
                        help='output directory to save the data in and save the created histograms')

    # parser argument for verbose printing and plotting
    parser.add_argument('-v', '--verbose', dest='verbose', default=True, action='store_true',
                        help='print some of the progress to the terminal')
    parser.add_argument('-g', '--histogram', dest='plotting', default=False, action='store_true',
                        help='create and save a histogram')

    # flags for weapon traits
    parser.add_argument('-pro', '--proven', dest='proven', default=False, type=int,
                        help='proven, minimal value of the damage die. '
                             'Must be a positive integer below amount of sides and above 1.')
    parser.add_argument('-a', '--accurate', dest='accurate', action='store_true', default=False,
                        help='accurate, adds extra damage die on high DoS. True or False.')
    parser.add_argument('-b', '--bonus', dest='bonus', default=0, type=int,
                        help='flat bonus to damage')
    parser.add_argument('-gr', '-graviton', dest='graviton', default=False, action='store_true',
                        help='graviton, adds extra damage based on the armour of the target')
    parser.add_argument('-p', '--penetration', dest='penetration', default=0, type=int,
                        help='penetration of the weapon, only works against armour on the enemy')
    parser.add_argument('-pri', '--primitive', dest='primitive', default=False, type=int,
                        help='primitive, maximum value of the damage die.'
                             'Must be smaller than sides and higher than 1')
    parser.add_argument('-u', '--unreliable', dest='unreliable', default=False, action='store_true',
                        help='unreliable, makes it so weapon jams on a 91 or  higher')
    parser.add_argument('-r', '--reliable', dest='reliable', default=False, action='store_true',
                        help='reliable, makes it so weapon only jams on a 100')
    parser.add_argument('-te', '--tearing', dest='tearing', default=False, action='store_true',
                        help='tearing, rolls 2 initial damage die and picks the higher')

    # selection of which enemy is being shot at
    parser.add_argument('-e', '--enemy', dest='enemy', default='hiver.txt', choices=listdir('enemy_presets'),
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
    if args.proven and args.primtive:
        parser.error("No weapon should have proven and primitive, that doesn't make sense")
    if args.reliable and args.unreliable:
        parser.error("No weapon can be both reliable and unreliable at the same time")
    if (args.proven < 2 or args.proven >= args.sides) and args.proven:
        parser.error("invalid number for proven")
    if (args.primitive >= args.sides or args.primitive < 2) and args.primitive:
        parser.error("invalid number for primitive")
    if args.sides < 2:
        parser.error("invalid number for sides")
    if args.n_rolls < 1:
        parser.error("n_rolls must be a positive integer")
    if args.target < 1:
        parser.error("target must be a positive integer")
    if args.penetration < 0:
        parser.error("penetration must be a positive number")

    return args


def damage_roll(DoS, accurate, proven, primitive, tearing, sides):
    """
    Rolls a single die with specified amount of sides
    proven is the minimum value of a die
    primitive is the max value of a die

    returns amount of damage (int)
    """
    # rolls 2 dice if tearing
    if tearing:
        roll = max(randint(1, sides), randint(1, sides))
    else:
        roll = randint(1, sides)

    # emperors fury check
    emperors_fury = False
    if roll == sides:
        emperors_fury = True

    # proven for min value and primitive for max
    if proven:
        if roll < proven:
            roll = proven
    if primitive:
        if roll > primitive:
            roll = primitive

    # adds extra damage die for accurate
    if accurate:
        if (DoS - 1) // 2 > 1:
            roll = roll + randint(1, sides)
        if (DoS - 1) // 2 > 2:
            roll = roll + randint(1, sides)

    return roll, emperors_fury


def determine_location(hit_roll):
    """"
    Given a hit roll, determines the location of the target hit following Dark Heresy 2 rules
    Only for persons, vehicles are handled from the parser
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


def hit_roller(target, proven, sides, accurate, primitive, tearing, reliable, unreliable, bonus, vehicle_facing):
    """"
    Determines if the attack hits
    returns a dict with:
        result (True/False)
        degrees (degrees of success if positive,
                negative if failure)
        location (string with location hit)
        hit_roll (int of original roll)
        damage (int, flat damage dealt before soak of target)
    """
    # rolls the set
    hit_roll = randint(1, 100)

    # set values for a success
    if hit_roll <= target:
        result = True
        degrees = target // 10 - hit_roll // 10 + 1
        damage, emperors_fury = damage_roll(DoS=degrees, accurate=accurate, proven=proven, primitive=primitive,
                                            tearing=tearing, sides=sides)
        damage += bonus
    # or a fail
    else:
        degrees = target // 10 - hit_roll // 10 - 1
        result = False
        damage = "miss"
        emperors_fury = False

    jam = check_jam(hit_roll, reliable, unreliable)

    if not vehicle_facing:
        location = determine_location(hit_roll)
    else:
        location = vehicle_facing

    # returns the result of the hit in a dict
    return {"result": result,
            "degrees": degrees,
            "location": location,
            "hit_roll": hit_roll,
            "damage": damage,
            "jam": jam,
            "fury": emperors_fury}


def dice_roller(n_dice, target, damage_bonus=0, penetration=0, vehicle_facing=False, accurate=False, primitive=False,
                tearing=False, razor_sharp=False, proven=False, unreliable=False, reliable=False, sides=10):
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
        rolls.append(hit_roller(target=target, proven=proven, sides=sides, accurate=accurate, primitive=primitive,
                                bonus=damage_bonus, reliable=reliable, unreliable=unreliable, tearing=tearing,
                                vehicle_facing=vehicle_facing))
        # razor sharp implementation
        if razor_sharp and rolls[i]['degrees'] > 2:
            rolls[i]["penetration"] = penetration * 2
        else:
            rolls[i]['penetration'] = penetration
    return rolls


def get_damage_dealt(hit_roll, enemy, graviton=False):
    """
    Calculates the exact damage dealt based on enemy armour values, original hit roll and some armour features.
    """
    # gets values from enemy and hit dict
    damage = hit_roll["damage"]
    armour = enemy[hit_roll["location"]]

    # checks graviton flag
    if graviton:
        damage = damage + armour

    # calculates damage
    soak = (enemy['toughness'] // 10) + max(armour - hit_roll["penetration"], 0)
    damage = max(damage - soak, 0)

    # inputs proper damage value into hit dict
    hit_roll["damage"] = damage
    return damage, hit_roll


def calculate_stats(rolls, graviton, enemy_stats):
    """
    Calculates a selection of stats such as
        hit rate (0-1)
        average damage per shot (float)
        average damage per hit (float)

    and returns a dict with those values
    """
    # initialises tracking variables
    hits = 0
    damage_sum = 0
    n_rolls = len(rolls)
    stats = {}
    max_damage = 0
    min_damage = 10000

    # loops over rolls to extract statistics
    for i in range(len(rolls)):
        if bool(rolls[i]["result"]):
            hits = hits + 1
            # calculates damage dealt
            damage_dealt, rolls[i] = get_damage_dealt(hit_roll=rolls[i], enemy=enemy_stats, graviton=graviton)
            damage_sum = damage_sum + damage_dealt
            if min_damage > damage_dealt:
                min_damage = damage_dealt
            if max_damage < damage_dealt:
                max_damage = damage_dealt

    # determines hit rate and damage per shot dealt
    stats["hit_rate"] = hits / n_rolls * 100
    stats["average_damage_shot"] = damage_sum / n_rolls
    stats["average_damage_hit"] = damage_sum / hits
    stats['min_damage'] = min_damage
    stats['max_damage'] = max_damage

    return stats


def verbose_printing(stats):
    """"
    verbose printing statements
    """
    print(f'hit rate was {stats.get("hit_rate")} %')
    print(f'average damage per shot was {stats.get("average_damage_shot")}')
    print(f"average damage per hit was {stats.get('average_damage_hit')}")
    print(f'minimal damage dealt on a hit was {stats.get("min_damage")}')
    print(f'maximum damage dealt on a hit was {stats.get("max_damage")}')


def main(args=False):
    """
    Runs the script given commands from argparser
    """
    if not args:
        args = parse_args()

    # loads enemy stats
    enemy_stats = load_enemy(args.enemy)

    # checks for proper inputs in the case of vehicle target
    input_checks(enemy_stats, args.facing)

    # loads weapon and rolls the dice
    if args.weapon:
        weapon = load_weapon(args.weapon)
        graviton = weapon["graviton"]
        rolls = dice_roller(n_dice=args.n_rolls, target=args.target, sides=args.sides, proven=weapon["proven"],
                            accurate=weapon["accurate"], damage_bonus=weapon["damage_bonus"], tearing=weapon['tearing'],
                            primitive=weapon["primitive"], penetration=weapon["penetration"],
                            unreliable=weapon['unreliable'], reliable=weapon['reliable'], vehicle_facing=args.facing)
    # or uses some base stats
    else:
        graviton = args.graviton
        rolls = dice_roller(n_dice=args.n_rolls, target=args.target, sides=args.sides, proven=args.proven,
                            accurate=args.accurate, damage_bonus=args.bonus, primitive=args.primitive,
                            penetration=args.penetration, unreliable=args.reliable, reliable=args.reliable,
                            tearing=args.tearing, vehicle_facing=args.facing,)

    # calculate stats
    stats = calculate_stats(rolls=rolls, graviton=graviton, enemy_stats=enemy_stats)

    if args.verbose:
        verbose_printing(stats)

    # TODO this is jank, fix it
    if args.output != 'False':
        with open(args.output, "w") as f:
            if args.weapon:
                f.write(dumps(weapon))
                f.write('\n')
            for i in range(len(rolls)):
                f.write(dumps(rolls[i]))
                f.write('\n')

    if args.plotting:
        plot_hist(rolls, args.output)


if __name__ == '__main__':
    main()

# welcome to the bottom of the file, thanks for checking out the code. Hope its comprehensive enough to understand.
# if you've got any suggestions or want to talk Python DM me on Discord - AxeldeAlex#9520
