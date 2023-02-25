import argparse
import sys
import os
import shutil
import json

import numpy as np
import pandas as pd

import pydicom
from rt_utils import RTStructBuilder
import surface_distance as sd


def is_empty(folder_path):
    """
    This function checks if a folder is empty or not.

    Parameters
    ----------
    folder_path : str
        Path to the folder that you want to check (Ex: "path/to/folder").

    Returns
    -------
    True :
        If the folder is empty the methods returns True.
    False :
        If the folder is not empty the methods returns False.

    """
    if len(os.listdir(folder_path)) == 0:
        return True
    else:
        return False
    
def patient_info(rtstruct_file_path,
                 information,
                 ):
    """
    This function extracts patient informations from RTSTRUCT file.

    Parameters
    ----------
    rtstruct_file_path : str
        Path to the RTSTRUCT.dcm file (Ex: "path/to/RTSTRUCT.dcm").
    information : str
        Name of the information that you want to extract from the RTSTRUCT.dcm
        file (Ex: "PatientID").

    Returns
    -------
    info:
        Value of the information required. The type of the value depends on
        the information extracted (Ex: str for PatientID; pydicom.uid.UID for
        FrameOfReferenceUID).

    """
    try:
        rtstruct_dataset = pydicom.dcmread(rtstruct_file_path)
        info = rtstruct_dataset[information].value
        return info
    except KeyError:
        sys.exit(f"There is no {information} in the RTSTRUCT file provided.")
        
def read_ct_slices(ct_folder_path):
    """
    This function creates the CT volume from the DICOM series.

    Parameters
    ----------
    ct_folder_path : str
        Path to the folder containing DICOM series files
        (Ex: path/to/CTfolder).

    Returns
    -------
    slices : list
        Ordered list of the slices that compose the CT volume.

    """
    ct_images = os.listdir(ct_folder_path)
    slices = []
    
    # Reading each ct image using pydicom and storing the results in a list.
    for ct_image in ct_images:
        ct_file_path = os.path.join(ct_folder_path,
                                    ct_image,
                                    )
        single_slice = pydicom.read_file(ct_file_path,
                                         force=True,
                                         )
        slices.append(single_slice)
        
    # Sorting every image in the list.
    slices = sorted(slices,
                    key=lambda x:x.ImagePositionPatient[2],
                    )
    return slices

def spacing_and_tolerance(ct_folder_path):
    """
    Computing voxel spacing of the loaded DICOM series.

    Parameters
    ----------
    ct_folder_path : str
        Path to the folder containing DICOM series files
        (Ex: path/to/CTfolder).

    Returns
    -------
    voxel_spacing_mm : list
        Voxel dimensions in millimeters.
    tolerance: float
        Greatest voxel dimension in millimeters.

    """
    # Creating CT volume
    slices = read_ct_slices(ct_folder_path)
    
    # Computing pixel spacing.
    pixel_spacing_mm = list(map(float,
                                slices[0].PixelSpacing._list,
                                ),
                            )
    
    # Computing slice thickness.
    slice_thickness_mm = float(slices[0].SliceThickness)
    
    # Computing voxel spacing.
    voxel_spacing_mm = pixel_spacing_mm.copy()
    voxel_spacing_mm.append(slice_thickness_mm)
    
    # Computing tolerance
    voxel_array = np.array(voxel_spacing_mm)
    tolerance = voxel_array.max()
    
    return voxel_spacing_mm, tolerance

def extract_all_segments(ct_folder_path,
                         rtstruct_file_path,
                         ):
    """
    Creates a list with the names of all segments in the current patient file.

    Parameters
    ----------
    ct_folder_path : str
        Path to the folder containing DICOM series files
        (Ex: path/to/CTfolder).
    rtstruct_file_path : str
        Path to the RTSTRUCT.dcm file (Ex: "path/to/RTSTRUCT.dcm").

    Returns
    -------
    all_segments : list
        List of all the segments in the current CT series
        (Ex. [Prostate, Bladder, Rectum])

    """
    # Reading current patient files.
    patient_data = RTStructBuilder.create_from(ct_folder_path, 
                                               rtstruct_file_path,
                                               )
    
    # Creating the list of all segments
    all_segments = patient_data.get_roi_names()
    
    return all_segments
    

def find_unknown_segments(all_segments,
                          config,
                          ):
    """
    Creates a list of current patient's segments that are not in the
    configuration file.

    Parameters
    ----------
    all_segments: list
        List of all the segments in the current CT series
        (Ex. [Prostate, Bladder, Rectum]).
    config : dict
        Dictionary containing lists of possible manual segments names.

    Returns
    -------
    unknown_segments : list
        List of segments names that are not in the configuration file.
        (Ex. Spinal cord, Brainstem)

    """
    # Creating the list that will contain the unkown segments
    unknown_segments = []
    
    # Finding the unkown segments and storing them in a list 
    for name in all_segments:
        if name in config["MBS segments"]:
            continue
        elif name in config["DL segments"]:
            continue
        elif name in config["External names"]:
            continue
        elif name in config["Prostate names"]:
            continue
        elif name in config["Rectum names"]:
            continue
        elif name in config["Bladder names"]:
            continue
        elif name in config["Left femur names"]:
            continue
        elif name in config["Right femur names"]:
            continue
        else:
            unknown_segments.append(name)
            
    return unknown_segments

def user_selection(unknown_segments,
                   config,
                   ):
    """
    Asking the user if uknown segments must be kept or not.
    
    Segments that are not in any list of the configuration file are shown to
    the user.
    If the user chooses to keep the segments he needs also to choose in which
    list of the configuration file they must be saved.
    Otherwise they will be discarded.

    Parameters
    ----------
    unknown_segments : list
        List of segments names that are not in the configuration file.
    config : dict
        Dictionary containing lists of possible manual segments names.

    Returns
    -------
    None.

    """
    # Asking to the user if the unknown segments must be kept or not, if yes
    # asking in which list of names they should be put.
    for name in unknown_segments:
        line = f"Do you want to keep {name}? Enter Y (yes) or N (no) \n"
        to_keep = input(line).upper()
        if to_keep == "Y":
            line1 = (f"To which alias name is {name} associated? Enter P")
            line2 = ("(Prostate), A (Anorectum), B (Bladder), L (Left")
            line3 = ("femur) R (Right femur) \n")
            what_is = input(line1+line2+line3).upper()
            if what_is == "P":
                config["Prostate names"].append(name)
                print(name,"added to Prostate names in config.json")
            elif what_is == "A":
                config["Rectum names"].append(name)
                print(name,"added to Rectum names in config.json")
            elif what_is == "B":
                config["Bladder names"].append(name)
                print(name,"added to Bladder names in config.json")
            elif what_is == "L":
                config["Left femur names"].append(name)
                print(name,"added to Left femur names in config.json")
            elif what_is == "R":
                config["Right femur names"].append(name)
                print(name,"added to Right femur names in config.json")
        elif to_keep == "N":
            continue
        
def extract_manual_segments(all_segments,
                            config,
                            ):
    """
    Creating the list of manual segments.
    
    The list of all segments in the image is extracted from patient data.
    Then, the manual_segments list is created starting from the list of alias
    names and is initially filled with zeros.
    Every element of all_segments is compared with the lists of names in the 
    config.json file and inserted in the correct place of the manual_segments
    list.

    Parameters
    ----------
    all_segments: list
        List of all the segments in the current CT series
        (Ex. [Prostate, Bladder, Rectum]).
    config : dict
        Dictionary containing lists of possible manual segments names.

    Returns
    -------
    manual_segments: list
        List containing current patient manual segments names.

    """
    # Creates the list of manual segments
    manual_segments = [0 for i in range(len(config["Alias names"]))]
    # Puts every manual segment in the correct place of the list
    for name in all_segments:
        if name in config["MBS segments"]:
            continue
        elif name in config["DL segments"]:
            continue
        elif name in config["External names"]:
            continue
        elif name in config["Prostate names"]:
            manual_segments[0] = name
        elif name in config["Rectum names"]:
            manual_segments[1] = name
        elif name in config["Bladder names"]:
            manual_segments[2] = name
        elif name in config["Left femur names"]:
            manual_segments[3] = name
        elif name in config["Right femur names"]:
            manual_segments[4] = name
        else:
            continue
        
    return manual_segments

def create_labelmap(ct_folder_path,
                    rtstruct_file_path,
                    segment_name,
                    ):
    """
    Creating the binary labelmap for the current segment.

    Parameters
    ----------
    ct_folder_path : str
        Path to the folder containing DICOM series files
        (Ex: path/to/CTfolder).
    rtstruct_file_path : str
        Path to the RTSTRUCT.dcm file (Ex: "path/to/RTSTRUCT.dcm").
    segment_name : str
        Name of the segment
        (Ex. "Prostate")
     
    Returns
    -------
    labelmap : numpy.ndarray
        3D binary array of the selected segment (0 out of the segment,
        1 inside).

    """
    # Reading current patient files.
    patient_data = RTStructBuilder.create_from(ct_folder_path, 
                                               rtstruct_file_path,
                                               )
    
    # Binary labelmap creation
    labelmap = patient_data.get_roi_mask_by_name(segment_name)
    
    return labelmap

def compute_metrics(reference_labelmap,
                    compared_labelmap,
                    ct_folder_path,
                    ):
    """
    Computing Hausdorff distance (hd), volumetric Dice similarity coefficient
    (dsc) and surface Dice similarity coefficient (sdsc).
    
    Starting from the binary labelmaps of the two segments the three metrics
    are computed.
    Surface Dice tolerance is set equal to the greatest voxel dimension.
    Percent value of Hausdorff distance is set to 95.
    

    Parameters
    ----------
    reference_labelmap: numpy.ndarray
        3D binary array of the reference segment.
    compared_labelmap: numpy.ndarray
        3D binary array of the segment to compare.
    voxel_spacing_mm : list
        Voxel dimensions (Ex. [1, 1, 3])

    Returns
    -------
    surface_dice : float
        Value of the surface Dice similarity coefficient between the two
        compared segments.
    volume_dice : float
        Value of the Dice similarity coefficient between the two compared
        segments.
    hausdorff_distance : float
        Value of the Hausdorff distance between the two compared segments.

    """
    # Computing voxel spacing and tolerance
    voxel_spacing_mm, tolerance = spacing_and_tolerance(ct_folder_path)
    
    # Metrics computation
    surf_dists = sd.compute_surface_distances(reference_labelmap,
                                              compared_labelmap,
                                              voxel_spacing_mm,
                                              )
    
   
    surface_dice = sd.compute_surface_dice_at_tolerance(surf_dists,
                                                        tolerance_mm=tolerance,
                                                        )
    
    volume_dice = sd.compute_dice_coefficient(reference_labelmap,
                                              compared_labelmap,
                                              )
    
    hausdorff_distance = sd.compute_robust_hausdorff(surf_dists,
                                                     percent=95,
                                                     )
    
    return surface_dice, volume_dice, hausdorff_distance

def store_patients(input_folder_path):
    """
    Searching input directory for patient folders and storing their names in
    a list.

    Parameters
    ----------
    input_folder_path : str
        Path to the folder where patients are stored.

    Returns
    -------
    patient_folders: list
        List containing the names of patient folders in the input directory.

    """
    patient_folders = []
    for folder in os.listdir(input_folder_path):
        # Only patient folders are needed, so, files are skipped.
        if not os.path.isfile(os.path.join(input_folder_path,folder)):
            patient_folders.append(folder)
            
    return patient_folders

def create_folder(parent_folder_path,
                  folder_name,
                  ):
    """
    Creating a new folder and returning the path to it.

    Parameters
    ----------
    parent_folder_path : str
        Path to the folder where the new one must be created.
    folder_name : str
        Name of the new folder.
     
    Returns
    -------
    new_folder_path: str
        Path to the new folder.

    """
    # Defining folder path
    new_folder_path = os.path.join(parent_folder_path,
                                   folder_name,
                                   )
    
    # Creating folder if does not exist
    try:
        os.mkdir(new_folder_path)
    except FileExistsError:
        pass
    
    return new_folder_path

def move_ct_rtstruct_files(patient_folder_path,
                           ct_folder_path,
                           rtstruct_folder_path,
                           ):
    """
    Moving CT files in the CT folder and RS files in the RTSTRUCT folder.
    Folders and different kind of files won't be moved.
    
    Parameters
    ----------
    patient_folder_path : str
        Path to the patient folder.
    ct_folder_path : str
        Path to the folder where CT files will be stored.
    rtstruct_folder_path : str
        Path to the folder where RTSTRUCT files will be stored.

    Returns
    -------
    None.

    """
    for file in os.listdir(patient_folder_path):
        file_path = os.path.join(patient_folder_path,
                                 file,
                                 )
        if not os.path.isfile(file_path):
            pass
        else:
            if not (file.startswith("CT") or file.startswith("RS")):
                pass
            elif file.startswith("CT"):
                shutil.move(file_path,
                            ct_folder_path,
                            )
            elif file.startswith("RS"):
                shutil.move(file_path,
                            rtstruct_folder_path,
                            )

def fill_ct_rtstruct_folders(patient_folder_path,
                             ct_folder_path,
                             rtstruct_folder_path,
                             ):
    """
    Filling CT and RTSTRUCT folders if both empty.
    Exiting if only one of the folder is empty.
    Going on with execution if both folders already have files inside.

    Parameters
    ----------
    patient_folder_path : str
        Path to the patient folder.
    ct_folder_path : str
        Path to the folder where CT files will be stored.
    rtstruct_folder_path : str
        Path to the folder where RTSTRUCT files will be stored.

    Returns
    -------
    None.

    """
    # If both CT and RTSTRUCT folders have files in them no action is needed.
    if not (is_empty(rtstruct_folder_path) or is_empty(ct_folder_path)):
        print("Both RTSTRUCT and CT folders have already files in them.",
              "Thus, no files will be moved",
              )
        pass
    # Filling CT and RTSTRUCT folders if both empty.
    elif (is_empty(rtstruct_folder_path) and is_empty(ct_folder_path)):
        print("Moving CT.dcm files into CT folder and RS.dcm files into",
              "RTSTRUCT folder",
              )
        move_ct_rtstruct_files(patient_folder_path,
                               ct_folder_path,
                               rtstruct_folder_path,
                               )
    # Exit to not mix different data.
    else:
        exit_if_empty(rtstruct_folder_path)
        exit_if_empty(ct_folder_path)
        
def check_new_folder_path(new_folder_path):
    """
    Checking if the user provided new_folder_path as argument.
    If yes the path wil be concerted to python style.

    Parameters
    ----------
    new_folder_path : str
        Path to the folder where patient folders will be moved after execution.

    Returns
    -------
    new_folder_path : str or bool
        Path to the folder where patient folders will be moved after execution
        converted into python path style.
        False if the argument was not provided by the user.

    """
    if new_folder_path == ".":
        print("New folder path has not been provided. Patient folders won't",
              "be moved after execution.",
              )
        new_folder_path = False
    else:
        # Convert to python path style.
        new_folder_path = new_folder_path.replace("\\", "/")
    
    return new_folder_path

def read_config(config_path):
    """
    Opening the configuration.json file

    Parameters
    ----------
    config_path : str
        Path to the configuration file.

    Returns
    -------
    config : dict
        Content of the configuration file.

    """
    fd = open(config_path)
    config = json.load(fd)
    
    return config

def exit_if_empty(folder_path):
    """
    Exiting from execution if the selected folder is empty.

    Parameters
    ----------
    folder_path : str
        Path to a folder.

    Returns
    -------
    None.

    """
    
    if not is_empty(folder_path):
        pass
    else:
        sys.exit(f"{folder_path} is empty, execution halted")
        
def exit_if_no_patients(input_folder_path,
                        patient_folders,
                        ):
    """
    Exiting from execution if there are no patient folders.

    Parameters
    ----------
    input_folder_path : str
        Path to the folder where patients are stored.
    patient_folders : list
        List of the folders in the input directory.

    Returns
    -------
    None.

    """
    if not len(patient_folders) == 0:
        pass
    else:
        sys.exit(print(f"{input_folder_path} does not contain folders.",
                  "Be sure to provide as input the folder that contains the",
                  "patients and not directly .dcm files.",
                  "Execution halted",
                  )
                 )
        
def extract_rtstruct_file_path(rtstruct_folder_path):
    """
    Extracting rtstruct file path.

    Parameters
    ----------
    rtstruct_folder_path : str
        Path to the RTSTRUCT folder.

    Returns
    -------
    rtstruct_file_path : str
        Path to the RS.dcm file.

    """
    for file in os.listdir(rtstruct_folder_path):
        rtstruct_file_path = os.path.join(rtstruct_folder_path,
                                          file,
                                          )
    
    return rtstruct_file_path

def create_segments_matrices(manual_segments,
                             config,
                             ):
    """
    Creating the reference segments and compared segments matrices to compare
    manual-MBS, manual-DL and MBS-DL methods.

    Parameters
    ----------
    manual_segments : list
        List of the manual segments.
    config : dict
        Dictionary containing lists of possible manual segments names.

    Returns
    -------
    ref_segs : list
        List of reference segments lists.
    comp_segs : list
        List of segments to compare lists.

    """
    ref_segs = [manual_segments,
                manual_segments,
                config["MBS segments"],
                ]
    comp_segs = [config["MBS segments"],
                 config["DL segments"],
                 config["DL segments"],
                 ]
    
    return ref_segs, comp_segs

def hausdorff_dice(input_folder_path,
                   config_path,
                   excel_path,
                   new_folder_path,
                   join_data,
                   ):
    """
    Computation of Hausdorff distance (hd), volumetric Dice similarity 
    coefficient (dsc) and surface Dice similarity coefficient (sdsc) 
    between manual and automatic segmentations for pelvic structures.

    Parameters
    ----------
    input_folder_path : str
        Path to the folder where patients are stored.
    config_path : str
        Path to the configuration json file.
    excel_path : str
        Path to the .xlsx file where data will be stored (if it is not already
        there it will be automatically created).
    new_folder_path : str
        Path where patient folders will be moved after execution.
    join_data : bool
        If true: join previously extracted data with the new ones.

    Returns
    -------
    None.

    """
    # Opening the json file where the lists of names are stored.
    config = read_config(config_path)
    
    # List where final data will be stored.
    final_data = []
    
    # If join_data is True, old data will be extracted from excel_path,
    # otherwise the old excel file will be overwritten.
    if join_data:
        try:
            # loading existing data.
            old_data = pd.read_excel(excel_path)
            print(f"Successfully loaded {excel_path}")
            excel_file_exist = 1
        except FileNotFoundError:
            # There is not an existing excel file in excel path.
            print(f"Failed to load {excel_path}, a new file will be created")
            excel_file_exist = 0
    else:
        print(f"Excel file at {excel_path} will be overwritten if already",
              "present, otherwise it will be created.",
              )
    
    # Input folder can not be empty.
    exit_if_empty(input_folder_path)
    
    # Input folder must contain patient folders, not directly .dcm files.
    patient_folders = store_patients(input_folder_path)   
    exit_if_no_patients(input_folder_path,
                        patient_folders,
                        )
    
    # Selecting one patient at the time and analyzing it.
    for patient_folder in patient_folders:
        patient_folder_path = os.path.join(input_folder_path,
                                           patient_folder,
                                           )
        
        # Patient folder can not be empty.
        exit_if_empty(patient_folder_path)
        
        # RTSTRUCT and CT series should be in different folders.
        # Creating RTSTRUCT folder if it is not already present, otherwise
        # going on with the execution.
        rtstruct_folder_path = create_folder(patient_folder_path,
                                             "RTSTRUCT",
                                             )
        
        # Creating CT folder if it is not already present, otherwise
        # going on with the execution.
        ct_folder_path = create_folder(patient_folder_path,
                                       "CT",
                                       )
        
        # Filling CT and RTSTRUCT folders if both empty
        fill_ct_rtstruct_folders(patient_folder_path,
                                 ct_folder_path,
                                 rtstruct_folder_path,
                                 )
        
        # If RTSTRUCT or CT folders are still empty there are no data.
        exit_if_empty(rtstruct_folder_path)
        exit_if_empty(ct_folder_path)
        
        # Extracting rtstruct file path.
        rtstruct_file_path = extract_rtstruct_file_path(rtstruct_folder_path)
            
        # Extraction of patient ID and frame of reference UID.
        patient_id = patient_info(rtstruct_file_path,
                                  "PatientID",
                                  )
        frame_of_reference_uid = patient_info(rtstruct_file_path,
                                              "FrameOfReferenceUID",
                                              )
        
        print(f"Starting patient {patient_id} analysis")
        
        # If the current study is already in the dataframe skip it, otherwise
        # every study will be analyzed. 
        if join_data:
            # If the current frame of reference is already in the excel file
            # we can move to the next one.
            if excel_file_exist:
                for frame_of_reference in old_data.loc[:,"Frame of reference"]:
                    if frame_of_reference == frame_of_reference_uid:
                        print(f"Study {frame_of_reference} of patient",
                              f"{patient_id} is alreday in the dataframe,",
                              "going to the next one",
                              )
                        frame_uid_in_old_data = True
                        break
                    else:
                        frame_uid_in_old_data = False
                if frame_uid_in_old_data:
                    # Moving patient folder to a different location if the
                    # destination folder does not exist it will be
                    # automatically created.
                    if new_folder_path:
                        shutil.move(patient_folder_path,
                                    os.path.join(new_folder_path,
                                                 patient_folder,
                                                 ),
                                    )
                        print(f"{patient_folder} successfully moved",
                              f"to {new_folder_path}",
                              )
                    else:
                        pass
                    continue
            else:
                # Without an old dataframe every patient will be analyzed.
                pass
            
        # Creating the list of all segments of current patient.
        all_segments = extract_all_segments(ct_folder_path,
                                            rtstruct_file_path,
                                            )
        
        # Creating manual segments list.
        print("Creating the list of manual segments")
        unknown_segments = find_unknown_segments(all_segments,
                                                 config,
                                                 )
        user_selection(unknown_segments,
                       config,
                       )
        manual_segments = extract_manual_segments(all_segments,
                                                  config,
                                                  )
        
        # Reference and compared segments lists.
        ref_segs, comp_segs = create_segments_matrices(manual_segments,
                                                       config,
                                                       )
        
        # Computing HD, DSC and SDSC for every segment in manual and MBS lists.
        for methods in range(len(config["Compared methods"])):
            print("Computing 95 percentile Hausdorff distance, Dice",
                  "similarity coefficient and surface Dice similarity",
                  f"coefficient between {config['Compared methods'][methods]}",
                  "segments",
                  )
            
            for segment in range(len(config["Alias names"])):
                #Create binary labelmaps for reference and to compare segments.
                ref_labelmap = create_labelmap(ct_folder_path,
                                               rtstruct_file_path,
                                               ref_segs[methods][segment],
                                               )
                comp_labelmap = create_labelmap(ct_folder_path,
                                                rtstruct_file_path,
                                                comp_segs[methods][segment],
                                                )
                
                # Computing surface Dice similarity coefficient (sdsc), Dice
                # similarity coefficient (dsc) and Hausdorff distance (hd).
                sdsc, dsc, hd = compute_metrics(ref_labelmap,
                                                comp_labelmap,
                                                ct_folder_path,
                                                )
                
                # Temporary list to store the current row of the final
                # dataframe.
                row_data = [patient_id,
                            frame_of_reference_uid,
                            config["Compared methods"][methods],
                            ref_segs[methods][segment],
                            comp_segs[methods][segment],
                            config["Alias names"][segment],
                            hd,
                            dsc,
                            sdsc,
                            ]
                
                # Adding the constructed row to final_data.
                final_data.append(row_data)
      
        # Moving patient folder to a different location, if the destination
        # folder does not exist it will be automatically created.
        if new_folder_path:
            shutil.move(patient_folder_path,
                        os.path.join(new_folder_path,
                                     patient_folder,
                                     ),
                        )
            print(f"{patient_folder} successfully moved to {new_folder_path}")
        else:
            pass
        
    # Creating the dataframe
    new_data = pd.DataFrame(final_data,
                            columns=["Patient ID",
                                     "Frame of reference",
                                     "Compared methods",
                                     "Reference segment name",
                                     "Compared segment name",
                                     "Alias name",
                                     "95% Hausdorff distance (mm)",
                                     "Volumetric Dice similarity coefficient",
                                     "Surface Dice similarity coefficient",
                                     ],
                            )
    
    if join_data:
        try:
            # Concatenating old and new dataframes.
            frames = [old_data,
                      new_data,
                      ]
            new_data = pd.concat(frames,
                                 ignore_index=True,
                                 )
            print("Old and new dataframe concatenated")
        except NameError:
            print("There is not an old dataframe, concatenation not performed")
        
    
    # Saving dataframe to excel.
    print("Saving data")
    new_data.to_excel(excel_path,
                      sheet_name="Data",
                      index=False,
                      )
     
    # Updating config.json.
    json_object = json.dumps(config,
                             indent=4,
                             )
    with open(config_path, "w") as outfile:
        outfile.write(json_object)
        
    print("Execution successfully ended")
       
def main(argv):
    """
    Computation of Hausdorff distance (hd), volumetric Dice similarity 
    coefficient (dsc) and surface Dice similarity coefficient (sdsc) 
    between manual and automatic segmentations for pelvic structures.

    Parameters
    ----------
    argv : char **
        Pointer to the pointer to the array where command line arguments are
        stored in the memory.

    Returns
    -------
    None.

    """                     
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(description 
                                     = "HD, volDSC and surfDSC computation")
    parser.add_argument(dest="input_folder_path",
                        metavar="input_path",
                        default=None,
                        help="Path to the folder where patients are stored",
                        )
    parser.add_argument(dest="config_path",
                        metavar="config_path",
                        default=None,
                        help="Path to the configuration json file",
                        )
    parser.add_argument(dest="excel_path",
                        metavar="excel_path",
                        default=None,
                        help=("""Path to the .xlsx file where data will be 
                              stored (if it is not already there it will be
                              automatically created)"""
                              )
                        ) 
    parser.add_argument("-n", "--new-folder",
                        dest="new_folder_path",
                        metavar="PATH",
                        default=".",
                        required=False,
                        help=("""Path where patient folders will be moved
                              after execution"""
                              )
                        )
    parser.add_argument("-j", "--join-data",
                        dest="join_data",
                        metavar="BOOL",
                        default=False,
                        required=False,
                        help=("""If true: join previously extracted data with
                              the new ones"""
                              )
                        )
    
    args = parser.parse_args(argv)
    
    # To better separate input from output messages
    print("\n")
    
    # Check if the user provided new_folder
    new_folder_path = check_new_folder_path(args.new_folder_path)
        
    # Convert to python path style.
    input_folder_path = args.input_folder_path.replace("\\", "/")
    config_path = args.config_path.replace("\\", "/")
    excel_path = args.excel_path.replace("\\", "/")
    
    # If true new data will be concatenated with old ones.
    join_data = args.join_data
    
    # Run hausdorff_dice
    hausdorff_dice(input_folder_path,
                   config_path,
                   excel_path,
                   new_folder_path,
                   join_data,
                   )
    
    
if __name__ == "__main__":
    main(sys.argv[1:])