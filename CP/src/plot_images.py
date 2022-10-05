"""
The following script allows to convert and plot the results obtained without rotation.

"""

from utils import convert_file, show_results
import os

SAVE_PATH = './out/solutionsNoRotation/Images/'
RESULT_PATH = './out/solutionsNoRotation/Converted/'
PATH_NO_ROTATION = './out/solutionsNoRotation/'

if __name__ == '__main__':
    # For each image, I first of all convert it, then I save the results.
    os.chdir("..")

    for instance in range(1, 41):
        print("Processing image: " + str(instance))

        os.chdir(PATH_NO_ROTATION)
        convert_file(str(instance) + ".txt")
        os.chdir("../..")

        show_results(instance, RESULT_PATH, SAVE_PATH, save_image=True, show_image=False)
