# Hausdorff Dice Computation
This program calculates 95 percentile Hausdorff distance (HD), volumetric Dice similarity coefficient (DSC) and surface Dice similarity coefficient (SDSC) between manually contoured and automatically contoured pelvic structures.
Particularly, it computes these metrics for five organs at risk (i.e. prostate, rectum, bladder, left femur and right femur) contoured in three different ways: manually, using a deep learning segmentation algorithm and using a model based segmentation algorithm.
The final output is stored in a .xlsx file.

![metrics](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgBvMhw2ZldlQbHbJrwLL5x0ijLdY9XQM-ww&usqp=CAU)

### Hausdorff distance
HD is the greatest of all distances from a point in one contour surface to the closest point in the other contour surface.

![Hausdorff](https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Hausdorff_distance_sample.svg/250px-Hausdorff_distance_sample.svg.png)

### Dice similarity coefficient
DSC measures the spatial overlap between two segmentation volumes and it ranges from 0 (no overlap) to 1 (perfect overlap).

SDSC is exactly the same with the difference that the overlap is measured between two segmentation surfaces.

![Dice](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrnfpehrVZMJLjRDVUWxEZ9_pW0RYUlkdhlw&usqp=CAU)

## Prerequisites
[python](https://www.python.org/downloads/): The entire program is written in python, thus, it must be installed to execute it (python versions previous to 3.9.1 and next to 3.9.16 were not tested).

[pydicom](https://pypi.org/project/pydicom/), [rt-utils](https://pypi.org/project/rt-utils/): To open and read dicom files the libraries pydicom and rt-utils must be installed.

[surface-distance](https://github.com/deepmind/surface-distance): To compute HD, DSC and SDSC the library surface-distance must be installed.

[git](https://git-scm.com/downloads): must be downloaded in order to clone the surface-distance repository from github.

[openpyxl](https://pypi.org/project/openpyxl/): To save data into .xlsx files openpyxl is needed.

[numpy](https://numpy.org/install/) and [pandas](https://pandas.pydata.org/docs/getting_started/install.html) are other required libraries.

## General informations
The main part of the program is stored in the [Main.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Main.py) script.

All the library functions of the program are stored in the [Hausdorff_Dice.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Hausdorff_Dice.py) script.

[patients](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/tree/master/patients) folder contains a CT scan downloded from the cancer imaging archive(https://www.cancerimagingarchive.net/) where the organs at risk were contoured manually and using a deep learning and a model based segmentation algorithms.

[tests](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/tree/master/tests) folder contains the data required to run [Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py).

[Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py) is the python script used for testing [Hausdorff_Dice.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Hausdorff_Dice.py).

[config.json](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/config.json) is a file containing the lists of manual segments names. If, running the script, new names for the five organs at risk are met they will be saved in this file.

## How to run
To run the program, the user has firstly to download the whole repository Hausdorff_Dice_Computation.
Then, the script Hausdorff_Dice.py can be run from command line by typing:

*python path\to\Main.py path\to\patients\folder path\to\config.json path\to\new_config.json path\to\excel_file.xlsx --new-folder path\to\the\folder\where\patients\will\be\moved --join-data True*

The first four arguments are required:
* *path\to\patients\folder*: Is the path to the folder where patients folders are stored. **Do not put here directly the path to the folder containing .dcm files!**;
* *path\to\config.json*: Is the path to [config.json](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/config.json), a file that stores some important parameters like segment names;
* *path\to\new_config.json*: Is the path to a new configuration file where the updated configuration data will be saved after executution (if the file does not exist it will be automatically created);
* *path\to\excel_file.sxlsx*: Is the path to the file where the data will be saved after execution. If the file does not exist in the specified path it will be automatically created.

The last two argument are optional:
* *--new-folder path\to\the\folder\where\patients\will\be\moved*: Is the path where patient folders will be moved after execution. If not specified patient folders will remain in *path\to\input\folder*;
* *--join-data True*: If *True*, the new data extracted will be appended to the ones already present in the excel file. if *False* (default), the data already in the excel file will be overwritten by the new ones.

## Testing
In order to run [Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py) both [Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py) file and [tests](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/tree/master/tests) folder must be downloaded.

After downloading [pytest](https://pypi.org/project/pytest/), all the tests can be run from command line from the directory containing tests folder by typing:

python -m pytest -v path/to/Tests.py
