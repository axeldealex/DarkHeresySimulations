from matplotlib import pyplot as plt
import numpy as np


def plot_hist(rolls):
    damage_nums = np.empty(0, dtype=int)
    for i in range(len(rolls)):
        if rolls['result']:
            damage_nums = np.append(damage_nums, rolls[i]['damage'])

    fig, ax = plt.subplots(10, 7)
    ax.hist(damage_nums)

    return fig, ax


def save_hist(fig, ax, filepath):
    plt.savefig(fig)
    pass

