import matplotlib.pyplot as plt
import numpy as np


INSTANCE_PATH = '../VLSI_instances/'
RESULT_PATH = "../out/"


def read_instance(n):
    """ Read one instance file and return a dict containing the values
    Args:
      n(int): number of the instance
    Returns:
      dict: containing the instance values
    """
    with open(INSTANCE_PATH + 'ins-' + str(n) + '.txt') as f:
        contents = f.read()
    f.close()

    contents = contents.splitlines()
    w = int(contents[0])
    n = int(contents[1])
    mtr = []
    for i in range(2, n + 2):
        mtr.append([int(x) for x in contents[i].split()])

    return {'w': w, 'n': n, 'mtr': mtr}


def write_results(num_instance, instance, h, corners_x, corners_y, rotation=False, rotated=[]):
    """ Write the results of the computed instance to a txt file
    Args:
      num_instance(int): number of the instance
      instance(dict): dictionary containing the values of the instance
      h(int): plate's height
      corners_x(list:int): list containing the x coordinate of the bottom-left corner for each block
      corners_y(list:int): list containing the y coordinate of the bottom-left corner for each block
      rotation(bool): true if the results were computed with rotation enabled, false otherwise
      rotated(list:bool): list containing for each block if it has been rotated,
                          the list must be empty if rotation is false

    """

    path = ''
    if rotation:
        path = RESULT_PATH + 'solutionRotation/out-rot-' + str(num_instance) + '.txt'
    else:
        path = RESULT_PATH + 'solutionNoRotation/out-' + str(num_instance) + '.txt'

    n = instance['n']
    w = instance['w']
    widths = instance['mtr'][:, 0]
    heights = instance['mtr'][:, 1]

    with open(path, 'w') as f:
        f.write(str(w) + " " + str(h) + "\n")
        f.write(str(n) + '\n')
        for i in range(n):
            if rotation and rotated[i]:
                f.write(str(heights[i]) + " " + str(widths[i]) + " "
                        + str(corners_x[i]) + " " + str(corners_y[i]) + "\n")
            else:
                f.write(str(widths[i]) + " " + str(heights[i]) + " "
                        + str(corners_x[i]) + " " + str(corners_y[i]) + "\n")
    f.close()


def show_results(num_instance, rotation=False, rotated=None, only_write_img = False):
    """ Function that read the txt file containing the solution for a single instance.
        Then, plot and save as image the result.
    Args:
      num_instance(int): number of the instance
      rotation(bool): true if the results were computed with rotation enabled, false otherwise
      rotated(list:bool): list containing for each block if it has been rotated,
                          the list must be empty if rotation is false

    """
    path = ''
    if rotation:
        path = RESULT_PATH + 'solutionRotation/out-rot-' + str(num_instance) + '.txt'
    else:
        path = RESULT_PATH + 'solutionNoRotation/out-' + str(num_instance) + '.txt'

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

    for k in range(2, n + 2):
        width, height, x, y = contents[k].split()
        widths.append(int(width))
        heights.append(int(height))
        corners_x.append(int(x))
        corners_y.append(int(y))

    title = 'Solution instance ' + str(num_instance)
    if rotation:
        title += ' with rotation'

    fig, ax = plt.subplots()
    fig.set_size_inches(420/25.4, 297/25.4)
    ax.set_title(title)

    for i in range(n):
        color = np.array(np.random.choice(range(30, 231), size=3))
        color = color / 255
        rect = plt.Rectangle((corners_x[i], corners_y[i]), widths[i], heights[i],
                             facecolor=color, edgecolor='black', linestyle='solid', linewidth=2.5)
        ax.add_patch(rect)

        if rotation and rotated[i]:
            circle = plt.Circle((corners_x[i] + widths[i] / 2, corners_y[i] + heights[i] / 2), 0.20, color='w',
                                zorder=10)
            ax.add_patch(circle)

    ax.set(xlim=(0, w), ylim=(0, h))
    ax.set_aspect('equal')
    ax.grid(color='black', linewidth=0.75, linestyle='--')

    plt.xticks(np.arange(0, w + 1, 1), rotation=90)
    plt.yticks(np.arange(0, h + 1, 1))

    path = ''
    if rotation:
        path = RESULT_PATH + 'solutionRotation/images/out-rot-' + str(num_instance) + '.png'
    else:
        path = RESULT_PATH + 'solutionNoRotation/images/out-' + str(num_instance) + '.png'
    plt.savefig(path)

    if not only_write_img:
        plt.show()

    plt.close()


def order_by_area(shape_matrix):
    """ function that sorts the matrix from largest to smallest using the area of each block
    Args:
      shape_matrix(matrix:int): matrix containing the shape of each block
    Returns:
      matrix: the sorted matrix
    """
    n = len(shape_matrix[:, 0])
    for i in range(n - 1):
        for j in range(i + 1, n):
            if (shape_matrix[i, 0] * shape_matrix[i, 1]) < (shape_matrix[j, 0] * shape_matrix[j, 1]):
                tmp = np.copy(shape_matrix[i])
                shape_matrix[i] = np.copy(shape_matrix[j])
                shape_matrix[j] = np.copy(tmp)

    return shape_matrix


def get_upper_bound(instance):
    """ Compute the upper bound for the plate
      Args:
        instance(dict): dictionary containing the values of the instance
      Returns:
        int: the computed upper bound for the plate
    """

    w = instance['w']
    n = instance['n']
    shape_matrix = instance['mtr']

    combination_indexes = [0]

    width_sum = shape_matrix[0][0]
    width_sum_no_last = 0

    for i in range(1, n):
        width_sum_no_last = width_sum
        width_sum += shape_matrix[i][0]

        if ((width_sum - 1) % w) < ((width_sum_no_last - 1) % w):
            combination_indexes.append(i)

    combination_indexes.append(n - 1)

    max_h = 0
    for i in range(len(combination_indexes) - 1):
        if combination_indexes[i] != combination_indexes[i + 1]:
            max_h += np.max(shape_matrix[combination_indexes[i]:(combination_indexes[i + 1]), 1])
        else:
            max_h += shape_matrix[combination_indexes[i], 1]

    return int(max_h)


def get_lower_bound(instance, rotation=False):
    """ Compute the lower bound for the plate
    Args:
      instance(dict): dictionary containing the values of the instance
      rotation(bool): true if rotation enabled, false otherwise
    Returns:
      int: the computed lower bound for the plate
    """
    w = instance['w']
    n = instance['n']
    shape_matrix = instance['mtr']
    min_h = 0
    for k in range(n):
        min_h += shape_matrix[k][0] * shape_matrix[k][1]
    min_h = np.ceil(min_h / w)

    if rotation:
        min_between_h_w = np.min([np.max(shape_matrix[:, 1]), np.max(shape_matrix[:, 0])])
        return int(np.max([min_h, min_between_h_w]))
    else:
        return int(np.max([min_h, np.max(shape_matrix[:, 1])]))


def prepare_instance(instance_num):
    """ Read one instance file, then sort the block by area and return a dictionary
        containing the instance's values
    Args:
      n(int): number of the instance
    Returns:
      dict: containing the instance values
    """

    instance = read_instance(instance_num)
    instance['mtr'] = order_by_area(np.asarray(instance['mtr']))
    return instance
