from z3 import *
import numpy as np
import itertools


# Creates the encoding of the model for a given instance, a given height.
# The parameter symmtry_breaking is used to set whether or not to add the symmetry breaking constraints
def SAT_encoding(instance, h, symmtry_breaking=False):
    w = instance['w']
    widths = instance['mtr'][:, 0]
    heights = instance['mtr'][:, 1]
    n = instance['n']

    g = Goal()

    # px and py are used to apply order encoding and they encode the fact that a block can have as first or second coordinate
    # the value of the second index.
    # e.g. px(i,z) means that the x-coordinate of the block i can be z.
    px = [[Bool(f"px{i + 1}_{x}") for x in range(w)] for i in range(n)]
    py = [[Bool(f"py{i + 1}_{y}") for y in range(h)] for i in range(n)]

    # Under and left are two matrices representing the fact that the block is below or at the left of another block
    # e.g. under(i,j) represents that block i is below block j. (Same thing for left)
    under = [[Bool(f"ud_{i + 1}_{j + 1}") if i != j else 0 for j in range(n)] for i in range(n)]
    left = [[Bool(f"lt{i + 1}_{j + 1}") if j != i else 0 for j in range(n)] for i in range(n)]

    # Each pair of block cannot overlap
    for i in range(n):
        for j in range(i + 1, n):
            g.add(Or(left[i][j], left[j][i], under[i][j], under[j][i]))

    # Clauses due to order ecoding
    for i in range(n):
        for e in range(0, w - widths[i]):
            g.add(Or(Not(px[i][e]), px[i][e + 1]))

        for f in range(0, h - heights[i]):
            g.add(Or(Not(py[i][f]), py[i][f + 1]))

        # Implicit clauses also due to order encoding
        for e in range(w - widths[i], w):
            g.add(px[i][e])

        for f in range(h - heights[i], h):
            g.add(py[i][f])

    for i in range(n):
        for j in range(n):
            if i != j:
                # left(i,j) -> xj > wi, lower bound for xj
                g.add(Or(Not(left[i][j]), Not(px[j][widths[i] - 1])))
                # under(ri,rj)-> yj > hi, lower bound for yj
                g.add(Or(Not(under[i][j]), Not(py[j][heights[i] - 1])))

                # 3-literals clauses for non overlapping, shown in the paper
                for e in range(0, w - widths[i]):
                    g.add(Or(Not(left[i][j]), px[i][e], Not(px[j][e + widths[i]])))
                for e in range(0, w - widths[j]):
                    g.add(Or(Not(left[j][i]), px[j][e], Not(px[i][e + widths[j]])))

                for f in range(0, h - heights[i]):
                    g.add(Or(Not(under[i][j]), py[i][f], Not(py[j][f + heights[i]])))
                for f in range(0, h - heights[j]):
                    g.add(Or(Not(under[j][i]), py[j][f], Not(py[i][f + heights[j]])))

    if symmtry_breaking:
        g.add(And(use_symmetry_breaking(n, w, h, widths, heights, px, py, left, under)))

    return g


# Contains the encoding of the symmetry breaking constraints
# n: number of blocks
# w: width of the plate
# h height of the plate
# widths: widths of the blocks
# height: heights of the blocks
# px: literals for ordering encoding
# py: literals for ordering encoding
# left: literals for posititoning relationship
# under: literals for posititoning relationship
def use_symmetry_breaking(n, w, h, widths, heights, px, py, left, under):
    domain_reduction_constraint = []
    # domain reduction constraint
    for i in range(int(np.floor((w - widths[0]) / 2))):
        domain_reduction_constraint.append(Not(px[0][i]))

    for j in range(int(np.floor((h - heights[0]) / 2))):
        domain_reduction_constraint.append(Not(py[0][j]))

    for rect in range(1, n):
        if widths[rect] > np.ceil((w - widths[0]) / 2):
            domain_reduction_constraint.append(Not(left[0][rect]))
        if heights[rect] > np.ceil((h - heights[0]) / 2):
            domain_reduction_constraint.append(Not(under[0][rect]))

    # Same size rectangles
    for (i, j) in itertools.combinations(range(n), 2):
        if widths[i] == widths[j] and heights[i] == heights[j]:
            domain_reduction_constraint.append(Not(left[j][i]))
            domain_reduction_constraint.append(
                Or(Not(under[j][i]), left[i][j])
            )

    return domain_reduction_constraint


# Creates the encoding of the model which allows to rotate the block for a given instance, a given height.
# The parameter symmtry_breaking is used to set whether or not to add the symmetry breaking constraints
def SAT_encoding_rotation(instance, h, symmtry_breaking=False):
    w = instance['w']
    widths = instance['mtr'][:, 0]
    heights = instance['mtr'][:, 1]
    n = instance['n']

    g = Goal()

    # px and py are used to apply order encoding and they encode the fact that a block can have as first or second
    # coordinate the value of the second index. e.g. px(i,z) means that the x-coordinate of the block i can be z.
    px = [[Bool(f"px{i + 1}_{x}") for x in range(w)] for i in range(n)]
    py = [[Bool(f"py{i + 1}_{y}") for y in range(h)] for i in range(n)]

    # Under and left are two matrices representing the fact that the block is below or at the left of another block
    # e.g. under(i,j) represents that block i is below block j. (Same thing for left)
    under = [[Bool(f"ud_{i + 1}_{j + 1}") if i != j else 0 for j in range(n)] for i in range(n)]
    left = [[Bool(f"lt{i + 1}_{j + 1}") if j != i else 0 for j in range(n)] for i in range(n)]

    rotated = [Bool(f"r_{i + 1}") for i in range(n)]

    # Each pair of block cannot overlap
    for i in range(n):
        for j in range(i + 1, n):
            g.add(Or(left[i][j], left[j][i], under[i][j], under[j][i]))

    # Clauses due to order ecoding
    for i in range(n):

        if heights[i] <= w:
            g.add(Or(And(Not(rotated[i]), *[Or(Not(px[i][e]), px[i][e + 1]) for e in range(0, w - widths[i])]),
                     And(rotated[i], *[Or(Not(px[i][e]), px[i][e + 1]) for e in range(0, w - heights[i])])))

            g.add(Or(And(Not(rotated[i]), *[Or(Not(py[i][f]), py[i][f + 1]) for f in range(0, h - heights[i])]),
                     And(rotated[i], *[Or(Not(py[i][f]), py[i][f + 1]) for f in range(0, h - widths[i])])))

            # Implicit clauses also due to order encoding
            g.add(Or(And(Not(rotated[i]), *[px[i][e] for e in range(w - widths[i], w)]),
                     And(rotated[i], *[px[i][e] for e in range(w - heights[i], w)])))

            g.add(Or(And(Not(rotated[i]), *[py[i][f] for f in range(h - heights[i], h)]),
                     And(rotated[i], *[py[i][f] for f in range(h - widths[i], h)])))
        else:
            g.add(Not(rotated[i]))
            g.add(*[Or(Not(px[i][e]), px[i][e + 1]) for e in range(0, w - widths[i])])
            g.add(*[Or(Not(py[i][f]), py[i][f + 1]) for f in range(0, h - heights[i])])
            # Implicit clauses also due to order encoding
            g.add(*[px[i][e] for e in range(w - widths[i], w)])
            g.add(*[py[i][f] for f in range(h - heights[i], h)])

    # (original_width = original_height) ==> rotated == False
    g.add([Not(rotated[i]) for i in range(n) if widths[i] == heights[i]])
    # original_height > plate_width ==> rotated == False
    g.add([Not(rotated[i]) for i in range(n) if heights[i] > w])

    # original_width > plate_height ==> rotated == False
    g.add([Not(rotated[i]) for i in range(n) if widths[i] > h])

    for i in range(n):
        for j in range(n):
            if i != j:

                if heights[i] <= w:
                    g.add(Or(And(Not(rotated[i]), Or(Not(left[i][j]), Not(px[j][widths[i] - 1]))),
                             And(rotated[i], Or(Not(left[i][j]), Not(px[j][heights[i] - 1])))))

                    # under(ri,rj)-> yj > hi, lower bound for yj
                    g.add(Or(And(Not(rotated[i]), Or(Not(under[i][j]), Not(py[j][heights[i] - 1]))),
                             And(rotated[i], Or(Not(under[i][j]), Not(py[j][widths[i] - 1])))))

                    # 3-literals clauses for non overlapping, shown in the paper
                    g.add(Or(And(Not(rotated[i]), *[Or(Not(left[i][j]), px[i][e], Not(px[j][e + widths[i]])) for e in
                                                    range(0, w - widths[i])]),
                             And(rotated[i], *[Or(Not(left[i][j]), px[i][e], Not(px[j][e + heights[i]])) for e in
                                               range(0, w - heights[i])])))

                    g.add(Or(And(Not(rotated[j]), *[Or(Not(left[j][i]), px[j][e], Not(px[i][e + widths[j]])) for e in
                                                    range(0, w - widths[j])]),
                             And(rotated[j], *[Or(Not(left[j][i]), px[j][e], Not(px[i][e + heights[j]])) for e in
                                               range(0, w - heights[j])])))

                    g.add(Or(And(Not(rotated[i]), *[Or(Not(under[i][j]), py[i][f], Not(py[j][f + heights[i]])) for f in
                                                    range(0, h - heights[i])]),
                             And(rotated[i], *[Or(Not(under[i][j]), py[i][f], Not(py[j][f + widths[i]])) for f in
                                               range(0, h - widths[i])])))

                    g.add(Or(And(Not(rotated[j]), *[Or(Not(under[j][i]), py[j][f], Not(py[i][f + heights[j]])) for f in
                                                    range(0, h - heights[j])]),
                             And(rotated[j], *[Or(Not(under[j][i]), py[j][f], Not(py[i][f + widths[j]])) for f in
                                               range(0, h - widths[j])])))

                else:
                    # left(i,j) -> xj > wi, lower bound for xj
                    g.add(Or(Not(left[i][j]), Not(px[j][widths[i] - 1])))
                    # under(ri,rj)-> yj > hi, lower bound for yj
                    g.add(Or(Not(under[i][j]), Not(py[j][heights[i] - 1])))
                    # 3-literals clauses for non overlapping, shown in the paper
                    g.add(*[Or(Not(left[i][j]), px[i][e], Not(px[j][e + widths[i]])) for e in range(0, w - widths[i])])

                    g.add(*[Or(Not(left[j][i]), px[j][e], Not(px[i][e + widths[j]])) for e in range(0, w - widths[j])])

                    g.add(
                        *[Or(Not(under[i][j]), py[i][f], Not(py[j][f + heights[i]])) for f in range(0, h - heights[i])])

                    g.add(
                        *[Or(Not(under[j][i]), py[j][f], Not(py[i][f + heights[j]])) for f in range(0, h - heights[j])])

        # Large rectangle constraints from the paper
    for (i, j) in itertools.combinations(range(n), 2):
        if widths[i] + widths[j] > w:
            g.add(Not(left[i][j]))
            g.add(Not(left[j][i]))
        if heights[i] + heights[j] > h:
            g.add(Not(under[i][j]))
            g.add(Not(under[j][i]))

    if symmtry_breaking:
        print('- add sb constraints')
        g.add(And(use_symmetry_breaking_rotation(n, w, h, widths, heights, px, py, left, under, rotated)))

    return g


# Contains the encoding of the symmetry breaking constraints in the case of rotation
# n: number of blocks
# w: width of the plate
# h height of the plate
# widths: widths of the blocks
# height: heights of the blocks
# px: literals for ordering encoding
# py: literals for ordering encoding
# left: literals for posititoning relationship
# under: literals for posititoning relationship
# rotated: literals to indicate a block is rotated 
def use_symmetry_breaking_rotation(n, w, h, widths, heights, px, py, left, under, rotated):
    domain_reduction_constraint = []
    # domain reduction constraint

    if heights[0] <= w:
        domain_reduction_constraint.append(
            Or(And(rotated[0], *[Not(px[0][i]) for i in range(int(np.floor((w - heights[0]) / 2)))]),
               And(Not(rotated[0]), *[Not(px[0][i]) for i in range(int(np.floor((w - widths[0]) / 2)))])))

        domain_reduction_constraint.append(
            Or(And(rotated[0], *[Not(py[0][j]) for j in range(int(np.floor((h - widths[0]) / 2)))]),
               And(Not(rotated[0]), *[Not(py[0][j]) for j in range(int(np.floor((h - heights[0]) / 2)))])))
    else:
        domain_reduction_constraint.append(And(*[Not(px[0][i]) for i in range(int(np.floor((w - widths[0]) / 2)))]))

        domain_reduction_constraint.append(And(*[Not(py[0][j]) for j in range(int(np.floor((h - heights[0]) / 2)))]))

    return domain_reduction_constraint
