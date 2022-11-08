PREREQUISITES

In order to test the LP model it is necessary to have AMPL installed, for the larger instances it is necessary a license activated. 


TESTING THE MODELS

1. In the folder ".\src\instances_and_model\" there are two .mod file one for the model with and one without rotation. There are also all the 40 instances already converted to be read by AMPL.
2. With the "querygenerator.py" script one can easily generate AMPL query either using gurobi or CPLEX as solver.
3. Finally paste your query in the command line of AMPL.


STRUCTURE OF THE FOLDER

	- collected_data: Constains results.xlsx file which show the obtained results discussed in the report. Moreover there are some .txt files with AMPL outputs of various tests.
	
	- original_instances: Contains the original instances .txt files.

	- src: Contains all the python scripts used to help during the realization of the project. In the ".\instances_and_model" folder there are the .mod model fil for AMPL and the converted instances in .dat format;

	- out: Contains all the results obtained. It is divided in two folders which have the same structure, the only difference is the fact that one has the results without the use of rotation. Inside each folder we have:
			- Some files named out-i.txt which contain the output produced by AMPL for instance i.
			- A folder named "img" containing all the plots of the solutions produced.
