from matplotlib import pyplot as plt
import numpy as np


def plot_hist(rolls, output_directory):
    damage_nums = np.empty(0, dtype=int)
    miss_count = 0
    for i in range(len(rolls)):
        if rolls[i]['result']:
            damage_nums = np.append(damage_nums, rolls[i]['damage'])
        else:
            miss_count += 1
    fig, ax = plt.subplots(1, 1)

    bins = max(damage_nums) - min(damage_nums) + 1
    counts, bins = np.histogram(damage_nums, bins=bins)
    ax.stairs(counts, bins, baseline=0.9*min(counts), label="Damage histogram")
    ax.legend()
    ax.set_title("Histogram of damage dealt")

    save_hist(fig, ax, output_directory)

    return None


def save_hist(fig, ax, filepath):
    plt.savefig(filepath)
    pass

