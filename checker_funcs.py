def check_jam(hit_roll, reliable, unreliable):
    """"
    Checks for a jam depending on the hit_roll and (un)reliable traits
    """
    if reliable and hit_roll == 100:
        return True
    elif unreliable and hit_roll >= 91:
        return True
    elif hit_roll > 96:
        return True
    return False


def input_checks(enemy_stats, facing):
    # checks if a facing is provided when it shouldn't be
    if enemy_stats['vehicle']:
        if not facing:
            raise ValueError("enemy is a vehicle but no facing is given\n"
                             "re-input with flag -f to give a facing.")
    else:
        if facing:
            raise ValueError("enemy is not a vehicle but a facing is given\n"
                             "re-input without -f to get results.")
