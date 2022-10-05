from z3 import *


def SAT_check(sat_encoding, time_limit=None):
    t = Then(
        Repeat(With(Tactic('simplify'), cache_all=True)),
        Repeat('propagate-values'),
        'symmetry-reduce',
        'sat-preprocess'
    )

    theory_solver = Tactic('psat')
    final_tactic = Then(t, theory_solver)

    s = final_tactic.solver()

    s.add(sat_encoding)

    if time_limit is not None:
        print('Solver timout: ', time_limit, 's')
        s.set("timeout", int(time_limit * 1000))

    if s.check() == sat:
        return True, s.model(), s.statistics()

    else:
        return False, None, s.statistics()


def converter_sat_coord(m, w, h, n, rotation=False):
    px = [[Bool(f"px{i + 1}_{x}") for x in range(w)] for i in range(n)]
    py = [[Bool(f"py{i + 1}_{y}") for y in range(h)] for i in range(n)]

    rotated_vars = [Bool(f"r_{i + 1}") for i in range(n)]
    rotated = []

    x_sol = []
    y_sol = []

    for i in range(n):
        if rotation:
            if m.evaluate(rotated_vars[i]) == True:
                rotated.append(True)
            else:
                rotated.append(False)

        j = 0
        while j < w:
            if m.evaluate(px[i][j]):
                x_sol.append(j)
                break
            j += 1

        j = 0
        while j < h:
            if m.evaluate(py[i][j]):
                y_sol.append(j)
                break
            j += 1

    return x_sol, y_sol, rotated
