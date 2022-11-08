import numpy as np;
import matplotlib.pyplot as plt
from pathlib import Path

RELATIVE_PATH = Path(__file__).parent

SOLUTIONS_PATH = str(RELATIVE_PATH) + '\\..\\out\\';

def show_results(num_instance, rotation, dirname):
    
    path = SOLUTIONS_PATH + dirname + '\\out-' + str(num_instance) + '.txt'

    with open(path) as f:
        contents = f.read()
    f.close()

    contents = contents.splitlines()
    w, h = contents[0].split()
    n = int(contents[1])
    w = int(w)
    h = int(h)

    widths = []
    heights = []
    corners_x = []
    corners_y = []
    rotated = []

    for k in range(2, n + 2):
        if rotation:
          width, height, x, y, r = contents[k].split()
          rotated.append(int(r))
        else:
          width, height, x, y = contents[k].split()
        widths.append(int(width))
        heights.append(int(height))
        corners_x.append(int(x))
        corners_y.append(int(y))
        

    title = 'Solution instance ' + str(num_instance)
    if rotation:
        for i in range (n):
          if rotated[i]:
            tmp = widths[i]
            widths[i] = heights[i]
            heights[i] = tmp
        title += ' with rotation'

    fig, ax = plt.subplots()
    ax.set_title(title)

    for i in range(n):
        color = np.array(np.random.choice(range(30, 231), size=3))
        color = color / 255
        rect = plt.Rectangle((corners_x[i], corners_y[i]), widths[i], heights[i],
                             facecolor=color, edgecolor='black', linestyle='solid', linewidth=1.5)
        ax.add_patch(rect)

        if rotation and rotated[i]:
            circle = plt.Circle((corners_x[i] + widths[i] / 2, corners_y[i] + heights[i] / 2), 0.20, color='w',zorder=10)
            ax.add_patch(circle)

    ax.set(xlim=(0, w), ylim=(0, h))
    ax.set_aspect('equal')
    ax.grid(color='black', linewidth=0.75, linestyle='--')

    plt.xticks(np.arange(0, w + 1, 1), rotation=90)
    plt.yticks(np.arange(0, h + 1, 1))

    path = ''
    if rotation:
        path = SOLUTIONS_PATH + dirname + '\\img\\out-rot-' + str(num_instance) + '.png'
    else:
        path = SOLUTIONS_PATH + dirname + '\\img\\out-' + str(num_instance) + '.png'
    fig.set_size_inches(420/25.4, 297/25.4)
    plt.savefig(path)
    plt.show()
    plt.close()


for i in range (1,41):
    show_results(i, True, 'best_gurobi_rotation')
