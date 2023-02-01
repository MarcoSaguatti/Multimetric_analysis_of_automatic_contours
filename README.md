# Hausdorff Dice Computation
This program calculates 95 percentile Hausdorff distance (HD), volumetric Dice similarity coefficient (DSC) and surface Dice similarity coefficient (SDSC) between manually contoured and automatically contoured pelvic structures.
Particularly, it computes these metrics for five organs at risk (i.e. prostate, rectum, bladder, left femur and right femur) contoured in three different ways: manually, using a deep learning segmentation algorithm and using a model based segmentation algorithm.
The final output is stored in a .xlsx file.

### Hausdorff distance
HD is the greatest of all distances from a point in one contour surface to the closest point in the other contour surface.
Let X and Y be two non-empty subsets of a metric space (M,d). We define their Hausdorff distance dH(X,Y) by

### Dice similarity coefficient

## General informations
All the code needed to run the program is stored in the [Hausdorff_Dice.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Hausdorff_Dice.py) script.

[patients](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/tree/master/patients) folder contains three patients where the organs at risk were contoured manually and using a deep learning and a model based segmentation algorithms.

[tests](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/tree/master/tests) folder contains the data required to run [Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py).

[Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py) is the python script used for testing [Hausdorff_Dice.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Hausdorff_Dice.py).

[config.json](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/config.json) is a file containing the lists of manual segments names. If running the script new names for the five organs at risk are met they will be saved in this file.

## Prerequisites
The entire program is written in [python](https://www.python.org/downloads/), thus, it must be installed to execute it (python versions previous to 3.9.1 and next to 3.9.16 were not tested).

To open and read dicom files the libraries [pydicom](https://pypi.org/project/pydicom/) and [rt-utils](https://pypi.org/project/rt-utils/) must be installed.

To compute HD, DSC and SDCS the library [surface-distance](https://github.com/deepmind/surface-distance) must be installed. Also [git](https://git-scm.com/downloads) must be downloaded in order to clone the repository from github.

To save data into .xlsx files [openpyxl](https://pypi.org/project/openpyxl/) is needed.

Other libraries required are [numpy](https://numpy.org/install/) and [pandas](https://pandas.pydata.org/docs/getting_started/install.html).

## How to run
To run the program, the user has firstly to download the whole repository Hausdorff_Dice_Computation.
Then, the script Hausdorff_Dice.py can be run from command line by typing:

python path\to\Hausdorff_Dice.py path\to\patients\folder path\to\config.json path\to\excel_file.xlsx --new-folder path\to\the\folder\where\patients\will\be\moved --join-data True

The first three arguments are required:
* *path\to\patients\folder*: Is the path to the folder where patients folders are stored. **Do not put here directly the path to the folder containing .dcm files!**;
* *path\to\config.json*: Is the path to [config.json](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/config.json), a file that stores some important parameters like segment names;
* *path\to\excel_file.sxlsx*: Is the path to the file where the data will be saved after execution. If the file does not exist in the specified path it will be automatically created.

The last two argument are optional:
* *--new-folder path\to\the\folder\where\patients\will\be\moved*: Is the path where patient folders will be moved after execution. If not specified patient folders will remain in *path\to\input\folder*;
* *--join-data True*: If *True*, the new data extracted will be appended to ones already present in the excel file. if *False* (default), the data already in the excel file will be overwritten by the new ones.

## Testing
In order to run [Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py) both [Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py) file and [tests](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/tree/master/tests) folder must be downloaded.

Then the follwing paths inside [Tests.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Tests.py) must be changed:
* *Path\to\tests\test_is_empty\empty_folder*: Is the path to an empty folder (any empty folder can be used);
* *Path\to\tests\test_is_empty\non_empty_folder*: Is the path to a non empty folder (any non empty folder can be used);
* *Path\to\tests\test_patient_info\RTSTRUCT\RS1.2.752.243.1.1.20230123144246076.4000.75633.dcm*: Is the path to the RTSTRUCT file contained in *tests\test_patient_info\RTSTRUCT*;
* *Path\to\tests\test_voxel_spacing\CT*: Is the path to the folder *tests\test_voxel_spacing_CT* that contains the dicom serie of one patient;
* *Path\to\config.json*: Is the path to the file *config.json*;
* *Path\to\tests\test_hausdorff_dice\input_folder*: Is the path to the folder *tests\test_hausdorff_dice\input_folder* that contains one patient to run *test_hausdorff_dice*;
* *Path\to\tests\test_hausdorff_dice\test.xlsx*: Is the path to *tests\test_hausdorff_dice\test.xlsx*, the excel file where the results of *test_hausdorff_dice* will be saved;
* *Path\to\tests\test_hausdorff_dice\new_folder*: Is the path to *tests\test_hausdorff_dice\new_folder*, the folder where patients will be moved after the execution of *test_hausdorff_dice*.

After downloading [pytest](https://pypi.org/project/pytest/), all the tests can be run from command line typing:

python -m pytest -v path/to/Tests.py