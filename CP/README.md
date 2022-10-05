PREREQUISITES

In order to test the instances it is necessary to have Minizinc installed. 
To test the models with OR-Tools it is also necessary to download and add it to minizinc solvers. The download link is: https://developers.google.com/optimization/install


TESTING THE MODELS

To test the models, it is necessary to:
	1. Open Minizinc using the chosen model (for example, to test the model for OR-Tools you need to open the "model_no_rotation - orTools.mzn" which has relative path, starting from this directory "./src/models/Or-Tools/");
	2. Use the solver configuration in the .mpc file which is in the folder of each solver;
	3. Open the instances we want to test, which are in the path: "./instances"


STRUCTURE OF THE FOLDER

	- collected_data: Constains additional .xlsx files which show the obtained results and some results of tests we made
	
	- instances: Contains the instances, both in .dzn and in .txt. The instances with the extension .txt, which were given are in the subfolder "/instances"

	- src: Contains all the python scripts created to create the plots and in the folder "models" there are all the Minizinc models created, which include:
			- A common model which does not use SB constraints;
			- A common model which does not use SB constraints in case rotation is allowed;
			- A folder for each solver which includes all the models and the configuration file.

	- out: Contains all the results obtained. It is divided in two folders which have the same structure, the only difference is the fact that one has the results without the use of rotation. Inside each folder we have:
			- Some files named i.txt which contain the output produced by Minizinc for instance i.
			- A folder named "Converted" which has all the outputs in the format required by the assignment
			- A folder named "Images" containing all the plots of the solutions produced.

