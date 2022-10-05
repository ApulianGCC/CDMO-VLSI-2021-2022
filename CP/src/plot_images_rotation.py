"""
The following script allows to plot the images and save them.

"""

import os

import numpy as np

from utils import convert_file, get_rotated_blocks_indexes, show_results

OUTPUT_PATH = './out/solutionsRotation/'
RESULT_PATH = './out/solutionsRotation/Converted/'
SAVE_PATH = './out/solutionsRotation/Images/'

INSTANCES_PATH = './instances/instances/'

os.chdir("..")

for instance in range(1, 40):
    rotated_blocks_indexes = []
    num_rotated = 0

    print("Processing image: " + str(instance))

    os.chdir(OUTPUT_PATH)
    convert_file(str(instance) + ".txt", rotation=True)
    os.chdir("../..")

    num_rotated, rotated_blocks_indexes, number_of_blocks = get_rotated_blocks_indexes(instance, INSTANCES_PATH,
                                                                                       RESULT_PATH)

    if num_rotated > 0:
        print("For this solution have been rotated: " + str(num_rotated) + " blocks")
        print("The indexes of the blocks which have been rotated is the following: " + str(rotated_blocks_indexes))

        rotated = np.zeros(number_of_blocks)
        rotated[rotated_blocks_indexes] = True
        show_results(instance, RESULT_PATH, SAVE_PATH, save_image=True, show_image=False, rotation=True,
                     rotated=rotated)
    else:
        print("For this solution no block has been rotated")
        show_results(instance, RESULT_PATH, SAVE_PATH, save_image=True, show_image=False, rotation=True, rotated=None)

    print()
