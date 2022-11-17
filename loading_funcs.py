def load_enemy(enemy_name):
    """"
    Loads enemy stats from a .txt file, in a pre-made location within the directory
    """
    enemy_fp = "enemy_presets/" + enemy_name
    enemy_stats = {}

    with open(enemy_fp, "r") as f:
        for line in f:
            if line.startswith('#'):
                pass
            else:
                split_line = line.strip("\n").split()
                enemy_stats[split_line[0]] = int(split_line[1])

    return enemy_stats


def load_weapon(weapon_name):
    """"
    Loads weapon stats from a .txt file, in a pre-made location within the directory
    """
    weapon_fp = "weapon_presets/" + weapon_name
    weapon_stats = {}

    # opens file
    with open(weapon_fp, "r") as f:
        for line in f:
            # skips over comments
            if line.startswith("#"):
                pass
            else:
                split_line = line.strip("\n").split()
                # checks conditions to make sure typing is correct
                if split_line[1] == 'True':
                    weapon_stats[split_line[0]] = True
                elif split_line[0] not in ['range', 'damage_bonus', 'penetration', 'clip']:
                    weapon_stats[split_line[0]] = split_line[1]
                else:
                    weapon_stats[split_line[0]] = int(split_line[1])

    # supplements the weapon dict with all supported weapon traits to ensure functionality down the line
    with open('supported_traits.txt', "r") as f:
        for line in f:
            if line.startswith("#"):
                pass
            else:
                supported_traits = line.strip("\n").split(",")

    # loops over all traits and adds entries if not present already
    keys = weapon_stats.keys()
    for trait in supported_traits:
        if trait not in keys:
            weapon_stats[trait] = False

    return weapon_stats
