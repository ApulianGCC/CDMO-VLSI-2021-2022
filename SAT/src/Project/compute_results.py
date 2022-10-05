import os
from utils import *
from SAT_encoding import *
from SAT_model import *


def solve_instances(instance_num, time_limit=None, rotation=False, symmetry_breaking=False, verbose=False, count=0):
    all_num_instances = []
    all_solutions = []
    all_is_optimal_solution = []
    all_statistics = []

    for i in instance_num:
        print('\n***Instance num: ', str(i), '***\n')

        all_num_instances.append(i)
        instance = prepare_instance(i)
        min_h = get_lower_bound(instance, rotation)
        max_h = get_upper_bound(instance)

        print('Plate width -> ', instance['w'])
        print('Min h -> ', min_h)
        print('Max h -> ', max_h)

        count_attempt = 1
        test_h = min_h
        model = None
        statistics = None
        time = 0

        while min_h <= test_h and test_h <= max_h:
            print('\n- Attempt num -> ', count_attempt)
            print(' - Tested h -> ', test_h)

            if rotation:
                print('- rotation enabled')
                encoding = SAT_encoding_rotation(instance, test_h, symmetry_breaking)
            else:
                encoding = SAT_encoding(instance, test_h, symmetry_breaking)

            if time_limit is not None:
                is_sat, model_tmp, statistics_tmp = SAT_check(encoding, time_limit - time)
            else:
                is_sat, model_tmp, statistics_tmp = SAT_check(encoding, None)

            time_tmp = statistics_tmp.get_key_value('time')
            time += time_tmp

            print('Expired time for this attempt -> ', time_tmp, 's')
            if is_sat != True:
                print('**UNSAT**')
                test_h += 1

            else:
                print('**SAT**')
                model = model_tmp
                statistics = statistics_tmp
                break

            count_attempt += 1

            if time_limit is not None and time >= time_limit:
                break

        if (time_limit is None or time <= time_limit) and model != None:
            print('Optimal solution founded in ', round(time, 3), 's, h -> ', test_h)

            all_is_optimal_solution.append(True)
            all_solutions.append(test_h)

            if verbose and statistics is not None:
                print('Statistics from z3 solver')
                print(statistics)

            all_statistics.append(statistics)

            corner_x, corner_y, rotated = converter_sat_coord(model, instance['w'], test_h, instance['n'], rotation)
            write_results(i, instance['w'], test_h, instance['n'], instance['mtr'][:, 0], instance['mtr'][:, 1],
                          corner_x, corner_y, rotation, rotated)
            show_results(i, rotation, rotated)

        else:
            print('No optimal solution in' + str(time_limit) + 's founded')
            all_is_optimal_solution.append(False)

            if model != None:
                print('Last suboptimal solution')

                if verbose and statistics is not None:
                    print('Statistics from z3 solver')
                    print(statistics)

                all_statistics.append(statistics)
                all_solutions.append(test_h)
                corner_x, corner_y, rotated = converter_sat_coord(model, instance['w'], test_h, instance['n'], rotation)
                write_results(i, instance['w'], test_h, instance['n'], instance['mtr'][:, 0], instance['mtr'][:, 1],
                              corner_x, corner_y, rotation, rotated)
                show_results(i, rotation, rotated)

            else:
                all_statistics.append(None)
                all_solutions.append(0)

    compute_statistics(rotation, symmetry_breaking, all_num_instances, all_solutions, all_is_optimal_solution,
                       all_statistics, count)


if __name__ == "__main__":
    os.chdir("../..")
    time_limit = 300
    instance_num = np.linspace(1, 39, 39, dtype=int)
    number_tests = 5
    for i in range(number_tests):
        solve_instances(instance_num, time_limit, rotation=False, symmetry_breaking=False, verbose=False, count=i + 1)
        solve_instances(instance_num, time_limit, rotation=False, symmetry_breaking=True, verbose=False, count=i + 1)
        solve_instances(instance_num, time_limit, rotation=True, symmetry_breaking=False, verbose=False, count=i + 1)
        solve_instances(instance_num, time_limit, rotation=True, symmetry_breaking=True, verbose=False, count=i + 1)
