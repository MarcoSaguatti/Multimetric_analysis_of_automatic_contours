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

![Dice](data:image/jpeg;base64,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)

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