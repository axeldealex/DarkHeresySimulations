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

    with open(weapon_fp, "r") as f:
        for line in f:
            if line.startswith("#"):
                pass
            else:
                split_line = line.strip("\n").split()
                weapon_stats[split_line[0]] = int(split_line[1])

    return weapon_stats
