import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import utility
import os.path

LIA = 'LIA'
IDL = 'IDL'
NOT_AND = 'NotAnd'


def compare_time_withSB(solver, formulation, rotation=False):
    title = '../collected_data/' + solver + '_' + formulation
    if rotation:
        title += '_withRotation_'
    else:
        title += '_noRotation_'
    title_sb = title
    title += 'noSymmetryBreaking - average.csv'
    title_sb += 'withSymmetryBreaking - average.csv'

    print(title)
    print(title_sb)

    df_noSB = pd.read_csv(title, delimiter=',', decimal=',')
    df_withSB = pd.read_csv(title_sb, delimiter=',', decimal=',')

    time_noSB = df_noSB['Time'].replace('Time-out', '300.00').str.replace(',', '.').str.replace('\*', '',regex=True).to_numpy(dtype=float)
    time_withSB = df_withSB['Time'].replace('Time-out', '300.00').str.replace(',', '.').str.replace('\*', '',regex=True).to_numpy(
        dtype=float)

    instance_num = np.linspace(1, 40, 40, dtype=int)

    width = 0.35
    fig, ax = plt.subplots()

    standard_timeout = np.array(time_noSB) >= 300
    standard_sat = np.array(time_noSB) < 300
    symmetry_timeout = np.array(time_withSB) >= 300
    symmetry_sat = np.array(time_withSB) < 300

    bar_standard_timeout = ax.bar(instance_num[standard_timeout] - width/2, time_noSB[standard_timeout], width,
                                  color='white', hatch='/////', edgecolor='#0277bd', linewidth=0)

    bar_standard_sat = ax.bar(instance_num[standard_sat] - width/2, time_noSB[standard_sat], width, label="No symmetry breaking", color='#0277bd')

    bar_symmetry_timeout = ax.bar(instance_num[symmetry_timeout] + width/2, time_withSB[symmetry_timeout], width,
                                  color='white', hatch='/////', edgecolor='#ff6f00', linewidth=0)
    bar_symmetry_sat = ax.bar(instance_num[symmetry_sat] + width/2, time_withSB[symmetry_sat], width, label="With symmetry breaking", color='#ff6f00')

    ax.set_ylabel('Average execution times (seconds)')
    ax.set_xlabel('Instances')
    ax.set_xticks(instance_num)
    ax.legend()


    fig.tight_layout()
    plt.yscale('log')
    #plt.ylim(0,301)
    #plt.xlim(0,41)
    plt.show()



def compare_timeouts(solver, formulation, rotation=False):
    title = '../collected_data/' + solver + '_' + formulation
    if rotation:
        title += '_withRotation_'
    else:
        title += '_noRotation_'
    title_sb = title
    title += 'noSymmetryBreaking - average.csv'
    title_sb += 'withSymmetryBreaking - average.csv'

    print(title)
    print(title_sb)

    df_noSB = pd.read_csv(title, delimiter=',', decimal=',')
    df_withSB = pd.read_csv(title_sb, delimiter=',', decimal=',')

    timeouts_noSB = df_noSB['Failures']
    timeouts_withSB = df_withSB['Failures']

    tmp = np.linspace(1, 40, 40, dtype=int)

    width = 0.35
    fig, ax = plt.subplots()

    instance_timeout = (np.array(timeouts_noSB) > 0) | (np.array(timeouts_withSB) > 0)
    ticks = tmp[instance_timeout]
    print('ticks', ticks)
    print(len(ticks))
    instance_num = np.linspace(1, len(ticks), len(ticks), dtype=int)
    print(instance_num)
    print(len(instance_num))



    bar_standard_sat = ax.bar(instance_num - width/2, timeouts_noSB[instance_timeout], width, label="No symmetry breaking", color='#0277bd')
    bar_symmetry_sat = ax.bar(instance_num  + width/2, timeouts_withSB[instance_timeout] , width, label="With symmetry breaking", color='#ff6f00')

    ax.axhline(5, color='red',  linestyle='--', linewidth=0.85)
    ax.grid(axis='y', color='black', linewidth=0.85, linestyle='--')
    ax.set_ylabel('Timeouts in 5 runs times')
    ax.set_xlabel('Instances')
    strTicks = [str(x) for x in ticks]
    print(strTicks)
    ax.set_xticks(instance_num)
    ax.set_xticklabels(strTicks, rotation='vertical')

    ax.legend()

    fig.tight_layout()
    #plt.yscale('log')
    plt.ylim(0,5.5)
    #plt.xlim(0,41)
    plt.show()


compare_time_withSB(IDL, NOT_AND, rotation=True)

compare_timeouts(IDL, NOT_AND, rotation=True)

