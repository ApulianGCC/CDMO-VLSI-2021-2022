"""
File containing all the utilities function needed
"""

import os
import matplotlib.pyplot as plt
import numpy as np

"""The following function is used to convert the file from the output generated from Minizinc (which has been copied 
and pasted on a .txt named with just the number of the instance) into the output required. The output generated is in 
the folder with the following relative path: "./Solutions__X__" and the result is then saved into a folder named 
Converted, which has the following path, starting from the one of this script "./Solutions__X__/Converted" and each file 
is saved with the following name: 

        "out-_INSTANCE_NUMBER_.txt"

 where _INSTANCE_NUMBER_ is substituted with the actual instance number,  e.g. "solution30.txt"
 In case this result comes from a rotated instance the name has the following syntax:

        "out-rot-_INSTANCE_NUMBER_.txt"
"""


def convert_file(filename, rotation=False):
    with open(filename) as fin:
        temp = fin.readline().split()
        w = temp[0]
        h = temp[1]
        n = fin.readline().split()[0]
        widths = fin.readline().split()
        heights = fin.readline().split()
        x = fin.readline().split()
        y = fin.readline().split()

    # Remove useless '[' and ']' output of minizinc
    widths[0] = widths[0].replace("[", "")
    widths[int(n) - 1] = widths[int(n) - 1].replace("]", "")
    heights[0] = heights[0].replace("[", "")
    heights[int(n) - 1] = heights[int(n) - 1].replace("]", "")
    x[0] = x[0].replace("[", "")
    x[int(n) - 1] = x[int(n) - 1].replace("]", "")
    y[0] = y[0].replace("[", "")
    y[int(n) - 1] = y[int(n) - 1].replace("]", "")

    # Remove commas from the lists
    for i in range(len(x)):
        widths[i] = widths[i].replace(",", "")
        heights[i] = heights[i].replace(",", "")
        x[i] = x[i].replace(",", "")
        y[i] = y[i].replace(",", "")

    os.chdir("./Converted")

    out_name = "out-"
    if rotation:
        out_name += "rot-"

    with open(out_name + filename, "w") as fout:
        fout.write(w + " " + h + "\n")
        fout.write(n + "\n")

        for i in range(len(x)):
            fout.write(widths[i] + " " + heights[i] + " " + x[i] + " " + y[i] + "\n")
    os.chdir("..")


"""
The following method allows to produce the plot of the instance, given its number

With the params save_image and show_image the user is allowed to handle those options freely
"""


def show_results(num_instance, result_path, save_path, save_image=False, show_image=True, rotation=False, rotated=None):
    out_name = 'out-'

    if rotation:
        out_name += 'rot-'

    with open(result_path+out_name + str(num_instance) + '.txt') as f:
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

    for k in range(2, n + 2):
        width, height, x, y = contents[k].split()
        widths.append(int(width))
        heights.append(int(height))
        corners_x.append(int(x))
        corners_y.append(int(y))

    title = 'Solution instance ' + str(num_instance)
    if rotation:
        title += ' with rotation'

    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_title(title)

    for i in range(n):
        color = np.array(np.random.choice(range(256), size=3))
        color = color / 255
        rect = plt.Rectangle((corners_x[i], corners_y[i]), widths[i], heights[i],
                             facecolor=color, edgecolor='black', linestyle='solid', linewidth=1.5)
        ax.add_patch(rect)

        if rotation and rotated is not None and rotated[i]:
            circle = plt.Circle((corners_x[i] + widths[i] / 2, corners_y[i] + heights[i] / 2), 0.20, color='w',
                                zorder=10)
            ax.add_patch(circle)

    ax.set(xlim=(0, w), ylim=(0, h))
    ax.set_aspect('equal')
    ax.grid(color='black', linewidth=0.75, linestyle='--')

    plt.xticks(np.arange(0, w + 1, 1))
    plt.yticks(np.arange(0, h + 1, 1))
    image_name = save_path + str(num_instance) + ".png"
    if save_image:
        fig.set_size_inches(420/25.4,297/25.4)
        plt.savefig(image_name, bbox_inches='tight')
    if show_image:
        plt.show()

    plt.close()


"""
The following function allows to obtain the list of the blocks, each one of them represented as [w,h], in decreasing 
order of area  

"""


def get_ordered_dimensions(filename):
    widths = []
    heights = []
    areas = []

    with open(filename) as fin:
        fin.readline()  # I don't need the first line
        n = int(fin.readline().split()[0])

        for i in range(n):
            temp = fin.readline().split()
            widths.append(int(temp[0]))
            heights.append(int(temp[1]))
            areas.append(int(temp[0]) * int(temp[1]))

    indexes_sorted = np.flip(np.argsort(areas))
    blocks_descending_order = []

    for i in indexes_sorted:
        blocks_descending_order.append([widths[i], heights[i]])

    return blocks_descending_order


"""
The following function allows to obtain the list of blocks obtained as output, each block is represented as [w,h]

"""


def get_obtained_results(filename):
    blocks = []

    with open(filename) as fin:
        fin.readline()  # I do not need the first line
        n = int(fin.readline().split()[0])

        for i in range(n):
            temp = fin.readline().split()
            blocks.append([int(temp[0]), int(temp[1])])

    return blocks


"""
The following method allows to obtain the number of rotated blocks and the indexes of the blocks which have been rotated
for a given instance.

"""


def get_rotated_blocks_indexes(instance_number, INSTANCE_PATH, RESULT_PATH):
    rotated_blocks_indexes = []
    num_rotated = 0

    instance_filename = INSTANCE_PATH + "ins-" + str(instance_number) + ".txt"
    output_filename = RESULT_PATH + "out-rot-" + str(instance_number) + ".txt"

    input_dimensions = get_ordered_dimensions(instance_filename)
    output_dimensions = get_obtained_results(output_filename)
    n = len(input_dimensions)

    for i in range(n):
        if input_dimensions[i][0] != output_dimensions[i][0]:
            rotated_blocks_indexes.append(i)
            num_rotated += 1

    return num_rotated, rotated_blocks_indexes, n
