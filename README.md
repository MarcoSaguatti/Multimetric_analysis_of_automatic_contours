# Hausdorff Dice Computation
This program calculates 95 percentile Hausdorff distance (HD), volumetric Dice similarity coefficient (DSC) and surface Dice similarity coefficient (SDSC) between manually contoured and automatically contoured pelvic structures.
Particularly, it computes these metrics for five organs at risk (i.e. prostate, rectum, bladder, left femur and right femur) contoured in three different ways: manually, using a deep learning segmentation algorithm and using a model based segmentation algorithm.
The final output is stored in a .xlsx file.

### Hausdorff distance
HD is the greatest of all distances from a point in one contour surface to the closest point in the other contour surface.
Let X and Y be two non-empty subsets of a metric space (M,d). We define their Hausdorff distance dH(X,Y) by

### Dice similarity coefficient

## Prerequisites
The entire program is written in [python](https://www.python.org/downloads/), thus, it must be installed to execute it (python versions previous to 3.9.1 and next to 3.9.16 were not tested).

To open and read dicom files the libraries [pydicom](https://pypi.org/project/pydicom/) and [rt-utils](https://pypi.org/project/rt-utils/) must be installed.

To compute HD, DSC and SDCS the library [surface-distance](https://github.com/deepmind/surface-distance) must be installed. Also [git](https://git-scm.com/downloads) must be downloaded in order to clone the repository from github.

To save data into .xlsx files [openpyxl](https://pypi.org/project/openpyxl/) is needed.

Other libraries required are [numpy](https://numpy.org/install/) and [pandas](https://pandas.pydata.org/docs/getting_started/install.html).

## How to run
All the code needed to run the program is stored in the [Hausdorff_Dice.py](https://github.com/MarcoSaguatti/Hausdorff_Dice_Computation/blob/master/Hausdorff_Dice.py) script.

To run it, the user has firstly to download the whole repository Hausdorff_Dice_Computation.
Then, the script Hausdorff_Dice.py can be run from command line by typing:

python path/to/Hausdorff_Dice.py path/to/patients/folder path/to/config.json path/to/excel_file.xlsx --new-folder path/to/the/folder/where/patients/will/be/moved --join-data True

The first three arguments are required:
* *path/to/patient/folder*: Is the path to the folder where patients folders are stored. **Do not put here directly the path to the folder containing .dcm files!**
* *path/to/config.json*: