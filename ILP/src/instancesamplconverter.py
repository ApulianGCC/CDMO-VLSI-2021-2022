import numpy as np;
from pathlib import Path

RELATIVE_PATH = Path(__file__).parent

INSTANCE_PATH = str(RELATIVE_PATH) + '\\..\\original_instances\\';
RESULT_PATH = str(RELATIVE_PATH) + '\\instances_and_model\\';

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

    return {'plate_width': w, 'circuit_num': n, 'shape_matrix': mtr}

def order_by_area(shape_matrix):

    n = len(shape_matrix[:,0])
    for i in range(n - 1):
        for j in range(i + 1, n):
            if (shape_matrix[i,0] * shape_matrix[i,1]) < (shape_matrix[j,0] * shape_matrix[j,1]):
                tmp = np.copy(shape_matrix[i])
                shape_matrix[i] = np.copy(shape_matrix[j])
                shape_matrix[j] = np.copy(tmp)

    return shape_matrix

def calc_bound(shape_matrix,w,n):
    min_h = 0
    
    for k in range(n):
        min_h += shape_matrix[k][0] * shape_matrix[k][1]
    min_h = np.ceil(min_h / w)
    
    combination_indexes = []
    combination_indexes.append(0)

    width_sum = shape_matrix[0][0]
    width_sum_no_last = 0

    for i in range(1, n):
        width_sum_no_last = width_sum
        width_sum += shape_matrix[i][0]
   
        if( ( (width_sum - 1 ) % w) < ( (width_sum_no_last - 1 )% w) ) :
            combination_indexes.append(i)

    combination_indexes.append(n-1)

    max_h = 0
    for i in range (len(combination_indexes) -1):
        if combination_indexes[i] != combination_indexes[i+1]:
            max_h += np.max(shape_matrix[combination_indexes[i]:(combination_indexes[i+1]),1])
        else:
            max_h += shape_matrix[combination_indexes[i],1]
    
    return min_h, max_h


def write_converted_instances(num_instance):
    instance = read_instance(num_instance)
    shape_matrix = order_by_area(np.array(instance['shape_matrix']))
    min_h, max_h = calc_bound(shape_matrix,instance['plate_width'],instance['circuit_num'])

    with open(RESULT_PATH + '' + 'ins-' + str(num_instance) + '.dat', 'w') as f:
        f.write("data;\n\n")
        f.write("param w := " + str(instance['plate_width']) + ";\n")
        f.write("param n := " + str(instance['circuit_num']) + ';\n')
        f.write("param min_h := " + str(int(min_h)) + ';\n')
        f.write("param max_h := " + str(int(max_h)) + ';\n\n')
        f.write("set BLOCKS := ")
        for i in range(instance['circuit_num']):
            f.write(str(i+1) + " ")
        f.write(";\n\n")
        f.write("param:\twidth\theight :=\n")
        for i in range(instance['circuit_num']):
            f.write("\t" + str(i+1) + "\t" + str(shape_matrix[i][0]) + "\t" + str(shape_matrix[i][1]))
            if(i==instance['circuit_num']-1):
                f.write(";")
            else:
                f.write("\n")
    f.close()
    
for i in range (1,41):
    write_converted_instances(i)
