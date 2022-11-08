PREREQUISITES

In order to test the instances it is necessary to have a Python interpreter installed, and the libraries z3-solver and XlsxWriter (it is possible to install them using pip). 


TESTING THE MODELS
It is possible to test the models both using the .ipynb file or using the code meant to run on personal machines.
To test the model using the .ipynb file it is necessary to:
	1. Open Google Colaboratory
	2. Upload the file "VLSI_SMT_colabNotebook.ipynb" which is located in the folder "./src/"
	3. Create the folder "unibo/CombinatorialProject" in the root of Google Drive.
	4. Inside the folder "CombinatorialProjecty" copy the folders "out", "VLSI_instances" and "collected_data"
	5. Run all the cells

To test the model using the python project, it is sufficient to run the script "experimentMain.py" which is in the folder "./src/"


STRUCTURE OF THE FOLDER

	- collected_data: Constains additional .xlsx files which show the obtained results and the results of each single test we made;
	
	- VLSI_instances: Contains the instances given;

	- src: Contains all the python scripts created to solve the problem and create the plots. As said before the file "VLSI_SMT_colabNotebook.ipynb" contains the notebook which can be run on Colab, whereas in the folder
		 Project there is the same code, but this can be used on a personal computer too.

	- out: Contains all the results obtained. It is divided in two folders which have the same structure, the only difference is the fact that one has the results without the use of rotation. Inside each folder we have:
			- Some files named out-i.txt which contain the output produced by the solver for instance i.
			- A folder named "images" containing all the plots of the solutions produced.

