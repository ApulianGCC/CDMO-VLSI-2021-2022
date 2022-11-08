from z3 import *
import numpy as np


def smt_encode(instance, h, rotation=False, symmtry_breaking=False):
    """ Function that encode the VLSI design problem of the specified instance
    Args:
      instance(dict): dictionary containing the values of the instance
      rotation(bool): true to enable blocks rotation, false otherwise
      symmtry_breaking(bool): true to use symmetry breaking constraints, false otherwise
    Returns:
      z3.Goal: goal object containing the smt encoding of the problem
    """
    w = instance['w']
    n = instance['n']

    widths_arr = instance['mtr'][:, 0]
    heights_arr = instance['mtr'][:, 1]

    # create Z3 variables to represent the VLSI design problem
    w_val = IntVal(w)
    h_val = IntVal(h)
    corner_x = [Int(f"x_{i}") for i in range(n)]
    corner_y = [Int(f"y_{i}") for i in range(n)]
    widths = [Int(f"w_{i}") for i in range(n)]
    heights = [Int(f"h_{i}") for i in range(n)]

    g = Goal()

    if rotation:
        print('- rotation enabled -')
        # create z3.Bool variables to allow block rotation
        rotated = [Bool(f'r_{i}') for i in range(n)]

        g.add([Or(And(Not(rotated[i]), widths[i] == int(widths_arr[i]), heights[i] == int(heights_arr[i])),
                  And(rotated[i], widths[i] == int(heights_arr[i]), heights[i] == int(widths_arr[i]))) for i in
               range(n)])


        # auxiliary constraints for rotation
  
        # (original_width = original_height) ==> rotated == False
        g.add([Not(And(int(widths_arr[i]) == int(heights_arr[i]), rotated[i])) for i in range(n)])\
  
        # original_height > plate_width ==> rotated == False
        g.add([Not(And(int(heights_arr[i]) > w , rotated[i])) for i in range(n)])

        # original_width > plate_heght ==> rotated == False
        g.add([Not(And(int(widths_arr[i]) > h , rotated[i])) for i in range(n)])


    else:
        g.add([And(widths[i] == int(widths_arr[i]), heights[i] == int(heights_arr[i])) for i in range(n)])

    # add boundary constraint for each block
    g.add([And(corner_x[i] >= 0, corner_y[i] >= 0,
               corner_x[i] <= w_val - widths[i], corner_y[i] <= h_val - heights[i])
           for i in range(n)])

    # no overlap constraint for each pair of blocks with NotAnd formulation
    g.add([Not(And(corner_x[i] - corner_x[j] <= widths[j] - 1,
                   corner_x[j] - corner_x[i] <= widths[i] - 1,
                   corner_y[i] - corner_y[j] <= heights[j] - 1,
                   corner_y[j] - corner_y[i] <= heights[i] - 1))
           for i in range(n) for j in range(i + 1, n)])

    '''
    # no overlap constraint for each pair of blocks with Or formulation
    g.add([Or( corner_x[i] - corner_x[j] <= - widths[i],
                corner_y[i] - corner_y[j] <= - heights[i],
                corner_x[j] - corner_x[i] <= - widths[j],
                corner_y[j] - corner_y[i] <= - heights[j])
            for i in range(n) for j in range(i+1, n)])
    '''

    if symmtry_breaking:
        print('- Adding symmetry breaking constraints')
        g.add(use_symmetry_breaking(n, w, h, widths, heights, corner_x, corner_y))

    return g


def use_symmetry_breaking(n, w, h, widths, heights, corner_x, corner_y):
    """ Return the encoding of the symmetry breaking constraint
    Args:
      n(int): blocks num
      w(int): plate's width
      h(int): plate's height
      widths(list:z3.Int): list of z3 variables representing block widths
      heights(z3.int): list of z3 variables representing block heights
      corner_x(list:int): list containing the x coordinate of the bottom-left corner for each block
      corner_y(list:int): list containing the y coordinate of the bottom-left corner for each block

    returns:
      z3.And: encoding of the symmetry breaking constraint

    """
    # fix the first block to the bottom-left of the second block
    # ordering_constraint = And( corner_x[0] <= corner_x[1], corner_y[0] <= corner_y[1])

    # Fix the first block in the bottom-left part of the plate
    width_bound = int(np.floor(w / 2))
    height_bound = int(np.floor(h / 2))
    reduce_domain_first_block = And(corner_x[0] <= width_bound, corner_y[0] <= height_bound)

    # Ordering constraint between block with same widths
    ordering_widths = [Implies(And(corner_x[i] == corner_x[j], widths[i] == widths[j]),
                               corner_y[i] <= corner_y[j])
                       for i in range(n) for j in range(i + 1, n)]

    # Ordering constraint between block with same heights
    ordering_heights = [Implies(And(corner_y[i] == corner_y[j], heights[i] == heights[j]),
                                corner_x[i] <= corner_x[j])
                        for i in range(n) for j in range(i + 1, n)]

    used_constraint = And(reduce_domain_first_block, *ordering_widths, *ordering_heights)

    return used_constraint


def smt_check(smt_encoding, time_limit=None):
    """ Function that checks if the encoding passed as input is satisfaible
    Args:
      smt_encoding(z3.Goal): encoding of VLSI design problem for an instance
      time_limit(int): time limit in second for the solver, None if the time limit is not needed
    Returns:
      bool: True if the encoding is satisfaible, false otherwise
      z3.model: the model if the encoding is satisfaible, None otherwise
      z3.statistics: the statistics collected by the solver
    """

    # preprocessing tactics in order to simplify the encoding passed as input
    t = Then(
        Repeat(With(Tactic('simplify'), cache_all=True)),
        Repeat('solve-eqs'),
        Repeat('propagate-ineqs'),
        Repeat('propagate-values'),
        'symmetry-reduce',
        'purify-arith'
    )

    # the theory solver used to solve the goal
    # theory_solver = Tactic('qflia')
    theory_solver = Tactic('qfidl')
    # theory_solver = Tactic('default')

    final_tactic = Then(t, theory_solver)
    s = final_tactic.solver()

    if time_limit is not None:
        print('Solver timout: ', time_limit, 's')
        s.set("timeout", int(time_limit * 1000))

    s.add(smt_encoding)

    if s.check() == sat:
        return True, s.model(), s.statistics()
    else:
        return False, None, s.statistics()


def get_solution(n, model, rotation=False):
    """ Function that decode the results from the model
      Args:
        n(int): blocks num
        model(z3.model): model that represents the solution found
        rotation(bool): true if the results were computed with rotation enabled, false otherwise

      Returns:
        corners_x(list:int): list containing the x coordinate of the bottom-left corner for each block
        corners_y(list:int): list containing the y coordinate of the bottom-left corner for each block

        rotated(list:bool): list containing for each block if it has been rotated,
                            the list is empty if rotation is false
    """

    corner_x_vars = [Int(f"x_{i}") for i in range(n)]
    corner_y_vars = [Int(f"y_{i}") for i in range(n)]
    widths_vars = [Int(f"w_{i}") for i in range(n)]
    heights_vars = [Int(f"h_{i}") for i in range(n)]
    rotated_vars = [Bool(f'r_{i}') for i in range(n)]

    corner_x = []
    corner_y = []
    widths = []
    heights = []
    rotated = []

    for i in range(n):
        corner_x.append(model.evaluate(corner_x_vars[i]).as_long())
        corner_y.append(model.evaluate(corner_y_vars[i]).as_long())
        widths.append(model.evaluate(widths_vars[i]).as_long())
        heights.append(model.evaluate(heights_vars[i]).as_long())

        if rotation:
            if model.evaluate(rotated_vars[i]) == True:
                rotated.append(True)
            else:
                rotated.append(False)
    return corner_x, corner_y, rotated

