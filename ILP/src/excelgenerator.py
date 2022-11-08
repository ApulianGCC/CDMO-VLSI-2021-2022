import xlsxwriter
from pathlib import Path

RELATIVE_PATH = Path(__file__).parent

def compute_statistics(filename, solver):

  title = str(RELATIVE_PATH) + '\\GeneratedExcel\\' + filename + '.xlsx'

  print(title)

  workbook = xlsxwriter.Workbook(title)
  worksheet = workbook.add_worksheet()

  # Add a bold format to use to highlight cells.
  bold = workbook.add_format({'bold': True})
  cell_format_red_bg = workbook.add_format({'bg_color': 'red'})
 
  # Write some data headers.
  worksheet.write('A1', 'Instance', bold)
  worksheet.write('B1', 'Time', bold)
  worksheet.write('C1', 'SimplexIteration', bold)
  worksheet.write('D1', 'Cuts', bold)
  worksheet.write('E1', 'Best solution', bold)

  time=[]
  solution=[]
  simplex_iteration=[]
  cuts=[]


  with open(str(RELATIVE_PATH) + '\\..\\Collected_data\\' + filename + '.txt', 'r') as file: 
      while True: 
          line = file.readline()
          if solver == 'cplex':
              if "simplex" in line:
                  simplex_iteration.append(line.partition(" MIP simplex")[0])
              if "nodes" in line:
                  cuts.append(line.partition(" branch-and-bound")[0])
          if solver == 'gurobi':
              if "simplex" in line:
                  simplex_iteration.append(line.partition(" simplex")[0])
              if "nodes" in line:
                  cuts.append(line.partition(" branch-and-cut")[0])
        
          if "_total_solve_elapsed_time" in line:
            time.append(line.partition("= ")[2].rstrip("\n"))
          if "solution" in line:
            solution.append(line.partition("objective ")[2].rstrip("\n"))
          
          if not line: 
              break


  start_row =  1
  for i in range(40):
    worksheet.write(start_row +i, 0, i+1)

    if time[i].find('300') == -1:
      worksheet.write(start_row +i, 1, time[i])
    else:
      worksheet.write(start_row +i, 1, 'TIMED OUT', cell_format_red_bg)

    worksheet.write(start_row +i, 2, simplex_iteration[i])
    worksheet.write(start_row +i, 3, cuts[i])
    worksheet.write(start_row +i, 4, solution[i])
    
  workbook.close()

compute_statistics('CPLEXRotationSymmetryOptions','cplex')