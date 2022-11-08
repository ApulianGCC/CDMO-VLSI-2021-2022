def query_generator(num_instance,solver,options,rotation):
    
    print('reset;')
    if rotation:
        print('model model_rotation.mod;')
    else :
        print('model model_no_rotation.mod;')
    print('data ins-' + str(num_instance) + '.dat;')
    if solver=='gurobi':
        if options:
            print("option gurobi_options 'method=1 nodemethod=0 mipfocus=2 presolve=2 cuts=2 timelim=300';")
        else:
            print("option gurobi_options 'timelim=300';")
    if solver=='cplex':
        if options:
            print("option cplex_options 'dualopt mipstartalg=1 predual=1 mipemphasis=2 mipcuts=2 time=300';")
        else:
            print("option cplex_options 'time=300';")
    if solver=='xpress':
        if options:
            print("option xpress_options 'maxtime=300';")
        else:
            print("option xpress_options 'maxtime=300';")
    print('solve;')
    if rotation:
        print ('print : w, h > out-' + str(num_instance) + '.txt;')
        print('print : n > out-' + str(num_instance) + '.txt;')
        print('print {a in BLOCKS}: width[a], height[a], X[a], Y[a], R[a] > out-' + str(num_instance) + '.txt;')
    else :
        print ('print : w, h > out-' + str(num_instance) + '.txt;')
        print('print : n > out-' + str(num_instance) + '.txt;')
        print('print {a in BLOCKS}: width[a], height[a], X[a], Y[a] > out-' + str(num_instance) + '.txt;')
    
    
    
for i in range (1,41):
    query_generator(i,'gurobi', False, False)