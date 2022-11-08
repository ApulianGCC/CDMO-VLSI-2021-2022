import xlsxwriter
import utility
import encodingFunctions


def solve_instances(num_instances, time_limit=None, rotation=False, symmetry_breaking=False, verbose=False, count=0):
    """ Function that allows to solve the specified instances with different configurations for the encoding and the solver.
          Furthermore, this function collects and saves all data in xlsx format
      Args:
        num_instances(list:int): list containing the number of instance to solve
        time_limit(int): time limit in second for the solver, None if the time limit is not needed
        rotation(bool): true to enable blocks rotation, false otherwise
        symmetry_breaking(bool): true to use symmetry breaking constraints, false otherwise
        verbose(bool): true to print the statistics collected by the solver, false otherwise
        count(int): num of the experiment

    """

    # list used to store all the data and statistics collected for every instance
    all_num_instances = []
    all_solutions = []
    all_is_optimal_solution = []
    all_statistics = []

    for i in num_instances:
        print('\n***Instance num: ', str(i), '***\n')

        all_num_instances.append(i)

        instance = utility.prepare_instance(i)
        min_h = utility.get_lower_bound(instance, rotation)
        max_h = utility.get_upper_bound(instance)

        print('Plate width -> ', instance['w'])
        print('Min h -> ', min_h)
        print('Max h -> ', max_h)

        count_attempt = 1;
        test_h = (min_h + max_h) // 2
        model = None
        statistics = None
        time = 0
        last_h = 0

        while (min_h <= test_h and test_h <= max_h):
            print('\n - Attempt num -> ', count_attempt)
            print(' - Tested h -> ', test_h)
            encoding = encodingFunctions.smt_encode(instance, test_h, rotation, symmetry_breaking)

            if time_limit != None:
                is_sat, model_tmp, statistics_tmp = encodingFunctions.smt_check(encoding, time_limit - time)
            else:
                is_sat, model_tmp, statistics_tmp = encodingFunctions.smt_check(encoding, None)

            time_tmp = statistics_tmp.get_key_value('time')
            time += time_tmp

            print('Expired time for this attempt -> ', time_tmp, 's')
            if is_sat:
                print('**SAT**')
                max_h = test_h - 1
                last_h = test_h
                test_h = (min_h + max_h) // 2
                model = model_tmp
                statistics = statistics_tmp
            else:
                print('**UNSAT**')
                min_h = test_h + 1
                test_h = (min_h + max_h) // 2

            count_attempt += 1

            if time_limit != None and time >= time_limit:
                break

        if (time_limit == None or time <= time_limit) and model != None:
            print('Optimal solution founded in ', round(time, 3), 's, h -> ', test_h)

            all_is_optimal_solution.append(True)
            all_solutions.append(last_h)

            if verbose and statistics is not None:
                print('Statistics from z3 solver')
                print(statistics)

            all_statistics.append(statistics)

            corner_x, corner_y, rotated = encodingFunctions.get_solution(instance['n'], model, rotation)

            utility.write_results(i, instance, last_h, corner_x, corner_y, rotation, rotated)
            utility.show_results(i, rotation, rotated)

        else:
            print('No optimal solution in' + str(time_limit) + 's founded')
            all_is_optimal_solution.append(False)

            if model != None:
                print('Last suboptimal solution')

                if verbose and statistics is not None:
                    print('Statistics from z3 solver')
                    print(statistics)

                all_statistics.append(statistics)
                all_solutions.append(last_h)

                corner_x, corner_y, rotated = encodingFunctions.get_solution(instance['n'], model, rotation)
                utility.write_results(i, instance, last_h, corner_x, corner_y, rotation)
                utility.show_results(i, rotation, rotated)
            else:
                all_statistics.append(None)
                all_solutions.append(0)

    # write the excel file containing all the information
    compute_statistics(rotation, symmetry_breaking, all_num_instances, all_solutions, all_is_optimal_solution,
                       all_statistics, count)


def compute_statistics(rotation, symmetry_breaking, all_num_instances, all_solutions, all_is_optimal_solution,
                       all_statistics, count):
    """ Function that allows to solve the specified instances with different configurations for the encoding and the solver.
          Furthermore, this function collects and saves all data in xlsx format
      Args:
        rotation(bool): true if blocks rotation was enabled, false otherwise
        symmtry_breaking(bool): true if symmetry breaking constraints were enabled, false otherwise
        all_num_instances(list:int): list containing the num of the solved instances
        all_solutions(list:int): List containing the last solution found
        all_is_optimal_solution(list:bool): list containing boolean to represent that the solution
                                            found was the optimal one for each instance
        all_statistics(list;z3.statistics): list containing the collected statistics by the solver for each instance
        count(int): num of the experiment

    """
    title = '../collected_data/' + str(count) + '-IDL_NotAnd'

    if rotation:
        title += '_With_rotation'
    else:
        title += '_no_rotation'

    if symmetry_breaking:
        title += '_with_symmetry_breaking'
    else:
        title += '_no_symmetry_breaking'

    title += '.xlsx'

    print(title)

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

        if all_statistics[i] is not None and 'conflicts' in all_statistics[i].keys():
            conflicts = int(all_statistics[i].get_key_value('conflicts'))
            worksheet.write(start_row + i, 2, conflicts)
        else:
            worksheet.write(start_row + i, 2, '-')

        if all_statistics[i] is not None and 'propagations' in all_statistics[i].keys():
            propagations = int(all_statistics[i].get_key_value('propagations'))
            worksheet.write(start_row + i, 3, propagations)
        else:
            worksheet.write(start_row + i, 3, '-')

    workbook.close()


if __name__ == '__main__':
    time_limit = 300
    # instance_num =np.linspace(1, 40, 40, dtype=int)
    instance_num = [1, 2, 3, 4, 5]
    num_run = 1

    for i in range(num_run):
        print('--- run num : ', i + 1, '***\n\n')
        solve_instances(instance_num, time_limit, rotation=False, symmetry_breaking=False, verbose=False, count=i + 1)
        solve_instances(instance_num, time_limit, rotation=False, symmetry_breaking=True, verbose=False, count=i + 1)
        solve_instances(instance_num, time_limit, rotation=True, symmetry_breaking=False, verbose=True, count=i + 1)
        solve_instances(instance_num, time_limit, rotation=True, symmetry_breaking=True, verbose=True, count=i + 1)

