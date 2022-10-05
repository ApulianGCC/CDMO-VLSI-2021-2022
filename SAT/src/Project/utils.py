import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter


INSTANCE_PATH = "./instances/"
RESULT_PATH = "./out/"
STATISTICS_PATH = "./collected_data/"

# Reads the instance number n
def read_instance(n):
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


# Writes the results of a given instance
def write_results(num_instance, w, h, n, widths, heights, corners_x, corners_y, rotation=False, rotated=[]):
    path = ''
    if rotation:
        path = RESULT_PATH + 'SolutionsRotation/sol-rot-' + str(num_instance) + '.txt'
    else:
        path = RESULT_PATH + 'SolutionsNoRotation/sol-' + str(num_instance) + '.txt'

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


# Allows to show the results of an instance
def show_results(num_instance, rotation=False, rotated=None):
    path = ''
    if rotation:
        path = RESULT_PATH + 'SolutionsRotation/sol-rot-' + str(num_instance) + '.txt'
    else:
        path = RESULT_PATH + 'SolutionsNoRotation/sol-' + str(num_instance) + '.txt'

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
    ax.set_title(title)

    for i in range(n):
        color = np.array(np.random.choice(range(30, 231), size=3))
        color = color / 255
        rect = plt.Rectangle((corners_x[i], corners_y[i]), widths[i], heights[i],
                             facecolor=color, edgecolor='black', linestyle='solid', linewidth=1.5)
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
        path = RESULT_PATH + 'SolutionsRotation/Images/sol-rot-' + str(num_instance) + '.png'
    else:
        path = RESULT_PATH + 'SolutionsNoRotation/Images/sol-' + str(num_instance) + '.png'
    plt.savefig(path)
    plt.show()
    plt.close()


"""Absolute value function for Z3 solver, order by area function for block"""


def order_by_area(shape_matrix):
    n = len(shape_matrix[:, 0])
    for i in range(n - 1):
        for j in range(i + 1, n):
            if (shape_matrix[i, 0] * shape_matrix[i, 1]) < (shape_matrix[j, 0] * shape_matrix[j, 1]):
                tmp = np.copy(shape_matrix[i])
                shape_matrix[i] = np.copy(shape_matrix[j])
                shape_matrix[j] = np.copy(tmp)

    return shape_matrix


# Computes the lower bound
def get_lower_bound(instance, rotation=False):
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


# Computes the upper bound
def get_upper_bound(instance):
    w = instance['w']
    n = instance['n']
    shape_matrix = instance['mtr']

    combination_indexes = []
    combination_indexes.append(0)

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


# Prepares a given instance
def prepare_instance(instance_num):
    instance = read_instance(instance_num)
    instance['mtr'] = order_by_area(np.asarray(instance['mtr']))
    return instance


def compute_statistics(rotation, symmetry_breaking, all_num_instances, all_solutions, all_is_optimal_solution,
                       all_statistics, count):
    title = STATISTICS_PATH + str(count) + '-SAT_default'
    propagations = 0

    if rotation:
        title += '_With_rotation'
    else:
        title += '_no_rotation'

    if symmetry_breaking:
        title += '_with_symmetry_breaking'
    else:
        title += '_no_symmetry_breaking'

    title += '.xlsx'

    workbook = xlsxwriter.Workbook(title)
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})
    cell_format_red_bg = workbook.add_format({'bg_color': 'red'})

    # Write some data headers.
    worksheet.write('A1', 'Instance', bold)
    worksheet.write('B1', 'Time', bold)
    worksheet.write('C1', 'Conflicts', bold)
    worksheet.write('D1', 'Propagations', bold)
    worksheet.write('E1', 'Best solution', bold)

    start_row = 1
    for i in range(len(all_num_instances)):
        worksheet.write(start_row + i, 0, all_num_instances[i])

        if all_is_optimal_solution[i]:
            time = round(all_statistics[i].get_key_value('time'), 3)
            worksheet.write(start_row + i, 1, time)
            worksheet.write(start_row + i, 4, all_solutions[i])
        else:
            worksheet.write(start_row + i, 1, 'Timeout', cell_format_red_bg)
            worksheet.write(start_row + i, 4, all_solutions[i], cell_format_red_bg)

        if all_statistics[i] is not None:
            if 'sat conflicts' in all_statistics[i].keys():
                conflicts = int(all_statistics[i].get_key_value('sat conflicts'))
                worksheet.write(start_row + i, 2, conflicts)
            else:
                worksheet.write(start_row + i, 2, '-')
            if 'sat propagations 2ary' in all_statistics[i].keys():
                propagations += int(all_statistics[i].get_key_value('sat propagations 2ary'))
            if 'sat propagations 3ary' in all_statistics[i].keys():
                propagations += int(all_statistics[i].get_key_value('sat propagations 3ary'))
            if 'sat propagations nary' in all_statistics[i].keys():
                propagations += int(all_statistics[i].get_key_value('sat propagations nary'))

        if propagations != 0:
            worksheet.write(start_row + i, 3, propagations)
        else:
            worksheet.write(start_row + i, 3, '-')

    workbook.close()
