### TODO List
#### Modules
* Upravit vsetky classy v outlier_detection podobne ako to je v Occurrences a MultDist

* Vdaka za spolupracu na tomto projekte, bolo tu velmi fajn a dufam ze sa este niekedy stretneme --Tomas 
#### Finalization part
* prepare readme file

# ----
# Project Template
# ----

# Execution module 

Directories and file structure

The structure of the executive module is very intuitive. It consists of the following folders: data, iostrategies, managers, manipulation, utils, and validation. 
Besides all of these folders, there is also the main function to run the framework and a text file requirements.txt where you can find all prerequisites for installing to be able to work with the framework. 
The first folder, data, stores input, output, and test data. 
Folder iostrategies serves to load input data from various types of files or database to a dataframe.  Similarly, it writes the data from dataframe into database or output files. 
Folder managers contains an abstract class manager.py from which the other manager classes inherit. They are responsible for proper work with data or modules and catching possible exceptions. 
The manipulation folder holds all the available modules for work with data. 
Folder utils contains further folders according to their functionality. It contains framework configuration setup, utilities for natural language processing, scoring evaluation and also data training. 
In addition, the utils folder contains a config_parser.py file which reads config file and stores all the values in config objects. Logger.py serves for log management. 
The last one, variable_context.py, stores all the variables used in program execution to a dictionary schema.  
The validation folder contains files to test the data correctness. 

Execution flow
For work with the framework, running the main.py function is needed. First, working directory is set, necessary packages are imported, and modules are loaded. 
After that ConfigParser and VariableContext are called to load configuration files and to store all the variables used in program execution. Input manager is called. 
Whenever any process starts or ends, there is a log message with date and time, so durations of all the processes are measured. 
Depending on the type of input data, corresponding loader is called, and loaded data validated. ModuleManager is called for searching, importing and handling modules stored in modules folder. 
After applying modules on input data, OutputManager is called. The next step after validation of output data is writing into desired output file or database. 
The function VariableContext is called again to store the output data and the OutputManager is terminated. The last message we get is the exit code the process finished with. 



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them. You can find them in requirements.txt file.

```
requirements.txt
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
pip install -r requirements.txt
```

or 

```
conda create -y --name new_evironment
conda install -f -y -q --name new_evironment -c conda-forge --file requirements.txt
conda activate new_evironment
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system. For testing purpose we are using pytests, which are stored in /validation/test directory. There you can find directories with tests for IO strategies, managers and utilities.  

### Break down into end to end tests

Explain what these tests test and why

* test_loader includes tests for validation of input file, its extension, columns and/or sheets, but also tests for config file and checks correctness of its key values
* test_writer also contains tests for config file validation and checks existence of dataframe that shoul be saved to file
* test_variable_context is used to test saving, loading, deleting and overwriting objects in variable manager and correctness of those operations

```
# Example of test_loader test, testing loading of not existing file:

@pytest.mark.skipif(os.path.exists(ConfigParser().TEST_DIRECTORY + "examplefile@#123.csv"),
                    reason="File examplefile@#123.csv exists in directory")
def test_not_existing_file_exception(self):
    # WHEN
    input_file = {"file_name": "examplefile@#123.csv",
                  "variable_name": "daco_df"}
    # THEN
    with pytest.raises(FileNotFoundError):
        CSVLoader(config=self.config, variables=self.variables).load(input_file)
```

## Deployment

TODO

Add additional notes about how to deploy this on a live system

In progress..

### Coding style and rules

While creating this framework, we were using PEP 8 style guidance for Python code and we used best practices to write readable, well-documented and easy-to-modify code. 


### User manual

TODO

Drop reference to full documentation to repository

```
Give an example
```

## Built With

TODO

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [BitBucket](http://bitbucket.org/) for code versioning. 

## Authors

* **Martin Brezani**
* **Tomas Babjak**

## License

This project is product of PwC Slovakia. All rights reserved. 

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
