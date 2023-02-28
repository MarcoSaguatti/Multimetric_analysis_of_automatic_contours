import argparse
import sys
import os
import shutil
import json
import tempfile
import math

import numpy as np
import pandas as pd
import pytest

import pydicom
from rt_utils import RTStructBuilder
import surface_distance as sd

import Hausdorff_Dice


def test_is_empty_with_empty_folder():
    """    
    GIVEN: an empty folder
    
    WHEN: running the function is_empty
    
    THEN: return True
    
    """
    # Create a temporary empty folder
    temp_empty_folder = tempfile.TemporaryDirectory()
    
    expected = True
    observed = Hausdorff_Dice.is_empty(temp_empty_folder.name)
    assert expected == observed
    
    # Remove the folder
    temp_empty_folder.cleanup()
    
def test_is_empty_with_non_empty_folder():
    """
    GIVEN: a non empty folder
    
    WHEN: running the function is_empty
    
    THEN: return False

    """
    # Path to a non empty folder
    non_empty_folder = r".\tests\test_is_empty\non_empty_folder"
    
    expected = False
    observed = Hausdorff_Dice.is_empty(non_empty_folder)
    assert expected == observed
    
def test_patient_info_with_patient_id():
    """
    GIVEN: an RTSTRUCT file
    
    WHEN: running the function patient_info asking for PatientID
    
    THEN: return the correct patient ID

    """
    # Path to the RTSTRUCT file
    rtstruct_file_path = r".\tests\test_patient_info\RTSTRUCT\RS_002.dcm"
    
    expected = "Pelvic-Ref-002"
    observed = Hausdorff_Dice.patient_info(rtstruct_file_path,
                                           "PatientID",
                                           )
    assert expected == observed
    
def test_patient_info_with_frame_of_reference_uid():
    """
    GIVEN: an RTSTRUCT file
    
    WHEN: running the function patient_info asking for FrameOfReferenceUID
    
    THEN: return the correct frame of reference UID

    """
    # Path to the RTSTRUCT file
    rtstruct_file_path = r".\tests\test_patient_info\RTSTRUCT\RS_002.dcm"
    
    UID = "1.3.6.1.4.1.14519.5.2.1.7085.2036.235949374640197733305184528698"
    expected = UID
    observed = Hausdorff_Dice.patient_info(rtstruct_file_path,
                                           "FrameOfReferenceUID",
                                           )
    assert expected == observed
    
def test_read_ct_slices_with_frame_of_reference_uid():
    """
    GIVEN: the path to the folder containing a CT series
        
    WHEN: running the function read_ct_slices
        
    THEN: all the slices should have the same frame of reference UID

    """
    # Path to CT series folder
    ct_folder_path = r".\tests\test_read_ct_slices\CT"
    
    # Expected behavior
    UID = "1.3.6.1.4.1.14519.5.2.1.7085.2036.235949374640197733305184528698"
    expected = [UID for i in range(163)]
    
    # Observed behavior
    slices = Hausdorff_Dice.read_ct_slices(ct_folder_path)
    observed = [slices[i].FrameOfReferenceUID for i in range(len(slices))]
    
    assert expected == observed
    
def test_spacing_and_tolerance():
    """
    GIVEN: the path to the folder containing a CT series
        
    WHEN: running the function voxel_spacing_and_tolerance
        
    THEN: return the correct voxel spacing and tolerance

    """
    # Path to CT series folder
    ct_folder_path = r".\tests\test_spacing_and_tolerance\CT"
    
    expected_spacing = [1.0, 1.0, 3.0]
    expected_tolerance = 3.0
    spacing, tolerance = Hausdorff_Dice.spacing_and_tolerance(ct_folder_path)
    
    assert math.isclose(expected_spacing[0], spacing[0])
    assert math.isclose(expected_spacing[1], spacing[1])
    assert math.isclose(expected_spacing[2], spacing[2])
    assert math.isclose(expected_tolerance, tolerance)
    
def test_extract_all_segment_with_patient_ref002():
    """
    GIVEN: a CT series and its RTSTRUCT file
        
    WHEN: running the function extract_all_segments
        
    THEN: the segments names are the expected ones
        
    """
    # Path to CT series folder
    ct_folder_path = r".\tests\test_extract_all_segments\CT"
    
    # Path to RTSTRUCT file
    rtstruct_file_path = r".\tests\test_extract_all_segments\RS_002.dcm"
    
    expected = ["Bladder_MBS",
                "FemoralHead (Left)_MBS",
                "FemoralHead (Right)_MBS",
                "Prostate_MBS",
                "Rectum_MBS",
                "Prostata",
                "Retto",
                "Vescica",
                "FemoreSinistro",
                "FemoreDestro",
                "External",
                "Prostate_DL",
                "Anorectum_DL",
                "Bladder_DL",
                "Femur_Head_L_DL",
                "Femur_Head_R_DL",
                ]
    observed = Hausdorff_Dice.extract_all_segments(ct_folder_path,
                                                   rtstruct_file_path,
                                                   )
    assert expected == observed
    
def test_find_unknown_segments_with_example_list():
    """
    GIVEN: a list of segments names and the configuration file path
        
    WHEN: running the function find_unknown_segments
        
    THEN: obtain a list with only those segments that are not in the
          configuration file

    """
    # Example list to test the function
    all_segments = ["Prostata",
                    "Vescica",
                    "DestroFemore",
                    "SinistroFemore",
                    "Retto",
                    ]
    
    # Configuration file
    config_path = r".\tests\test_find_unknown_segments\config.json"
    fd = open(config_path)
    config = json.load(fd)
    
    expected = ["DestroFemore",
                "SinistroFemore",
                ]
    observed = Hausdorff_Dice.find_unknown_segments(all_segments,
                                                    config,
                                                    )
    
    assert expected == observed
    
def test_extract_manual_segments_with_example_list():
    """
    GIVEN: a list of segments names and the configuration file path
        
    WHEN: running the function extract_manual_segments
        
    THEN: obtain a list with only the five manual segments ordered in the
          correct way

    """
    # Example list to test the function
    all_segments = ["Prostata",
                    "Vescica",
                    "Anorectum_DL",
                    "FemoreSinistro",
                    "Retto",
                    "FemoreDestro",
                    "Bladder_MBS",
                    ]
    
    # Configuration file
    config_path = r".\tests\test_extract_manual_segments\config.json"
    fd = open(config_path)
    config = json.load(fd)
    
    expected = ["Prostata",
                "Retto",
                "Vescica",
                "FemoreSinistro",
                "FemoreDestro",
                ]
    observed = Hausdorff_Dice.extract_manual_segments(all_segments,
                                                      config,
                                                      )
    
    assert expected == observed
    
def test_compute_metrics():
    """
    GIVEN: The CT series folder, the RTSTRUCT file and two segments names
        
    WHEN: running the function compute_metrics
        
    THEN: obtain the correct surface Dice similarity coefficient, the
          correct Dice similarity coefficient and the correct Hausdorff
          distance

    """
    # Path to CT series folder and RTSTRUCT file
    ct_folder_path = r".\tests\test_compute_metrics\CT"
    rtstruct_file_path = r".\tests\test_compute_metrics\RS_002.dcm"
    
    # Extracting reference segment and segment to compare labelmaps
    ref_labelmap = Hausdorff_Dice.create_labelmap(ct_folder_path,
                                                  rtstruct_file_path,
                                                  "Vescica",
                                                  )
    comp_labelmap = Hausdorff_Dice.create_labelmap(ct_folder_path,
                                                   rtstruct_file_path,
                                                   "Bladder_MBS",
                                                   )
    
    expected_surface_dice = 0.9049208597597801
    expected_dice = 0.8680934291194945
    expected_hausdorff = 4.242640687119285
    sdsc, dsc, hd = Hausdorff_Dice.compute_metrics(ref_labelmap,
                                                   comp_labelmap,
                                                   ct_folder_path,
                                                   )
    
    assert math.isclose(expected_surface_dice,
                        sdsc,
                        )
    assert math.isclose(expected_dice,
                        dsc,
                        )
    assert math.isclose(expected_hausdorff,
                        hd,
                        )
    
def test_store_patients():
    """
    GIVEN: the path of a directory containing one patient folder and some
           DICOM files
        
    WHEN: running the function store_patients 
        
    THEN: return a list containing only the name of the patient folder

    """
    #Path to the directory containing patient folders
    input_folder_path = r".\tests\test_store_patients"
    
    expected = ["Pelvic-Ref002"]
    observed = Hausdorff_Dice.store_patients(input_folder_path)
    
    assert expected == observed
    
def test_create_folder_with_existing_folder():
    """
    GIVEN: the path to an already existing folder
        
    WHEN: running the function create folder
        
    THEN: the output folder path is returned

    """
    #Path to the parent directory
    parent_folder_path = r".\tests\test_create_folder"
    
    expected = r".\tests\test_create_folder\CT"
    observed = Hausdorff_Dice.create_folder(parent_folder_path,
                                               "CT",
                                               )
    
    assert expected == observed
    
def test_create_folder_with_non_existing_folder():
    """
    GIVEN: the path to a non existing folder
        
    WHEN: running the function create folder
        
    THEN: the output folder path is returned

    """
    # Create a temporary empty folder
    temp_folder = tempfile.TemporaryDirectory()
    
    expected = temp_folder.name+"\RTSTRUCT"
    observed = Hausdorff_Dice.create_folder(temp_folder.name,
                                            "RTSTRUCT",
                                            )
    
    assert expected == observed
    
    # Remove the folder
    temp_folder.cleanup()
    
# # FIXME: does not work
# def test_move_ct_rtstruct_files():
#     """
#     GIVEN: a patient folder path and the path to the CT and RTSTRUCT
#            directories inside it
        
#     WHEN: running the function move_ct_rtstruct_files
        
#     THEN: CT files will be moved into the CT folder, RS files will be moved
#           into the RTSTRUCT folder, other files will not be moved.
        
#     """
#     # Patient folder path
#     patient_folder_path = r".\tests\test_move_ct_rtstruct_files"
#     # CT folder path
#     ct_folder_path = patient_folder_path+"\CT"
#     # RTSTRUCT folder path
#     rtstruct_folder_path = patient_folder_path+"\RTSTRUCT"
    
#     # Check CT file initial path
#     expected_ct_start = patient_folder_path+"CT_move_test.dcm"
#     assert os.path.exists(expected_ct_start) == True
#     # Check RS file initial path
#     expected_rs_start = patient_folder_path+"RS_move_test.dcm"
#     assert os.path.exists(expected_rs_start) == True
#     # Check non CT and non RS file initial path
#     expected_txt_start = patient_folder_path+"txt_move_test.txt"
#     assert os.path.exists(expected_txt_start) == True
    
#     # Moving files
#     Hausdorff_Dice.move_ct_and_rtstruct_files(patient_folder_path,
#                                               ct_folder_path,
#                                               rtstruct_folder_path,
#                                               )
    
#     # Check CT file final path
#     expected_ct_end = ct_folder_path+"CT_move_test.dcm"
#     assert os.path.exists(expected_ct_end) == True
#     # Check RS file final path
#     expected_rs_end = rtstruct_folder_path+"RS_move_test.dcm"
#     assert os.path.exists(expected_rs_end) == True
#     # Check non CT and non RS file final path
#     expected_txt_end = patient_folder_path+"txt_move_test.txt"
#     assert os.path.exists(expected_txt_end) == True
    
#     # Restoring files initial positions
#     shutil.move(expected_ct_end,
#                 patient_folder_path,
#                 )
#     shutil.move(expected_rs_end,
#                 patient_folder_path,
#                 )
    
def test_check_new_folder_path():
    """
    GIVEN: the path to a folder
        
    WHEN: running the function check_new_folder_path
        
    THEN: return the path to the folder in python style

    """
    # Create a temporary empty folder
    folder_path = r".\tests\test_check_new_folder"
    
    expected = r"./tests/test_check_new_folder"
    observed = Hausdorff_Dice.check_new_folder_path(folder_path)
    
    assert expected == observed
    
def test_check_new_folder_path_without_folder():
    """
    GIVEN: the default value of new_folder_path
        
    WHEN: running the function check_new_folder_path
        
    THEN: return False

    """
    # Create a temporary empty folder
    folder_path = "."
    
    expected = False
    observed = Hausdorff_Dice.check_new_folder_path(folder_path)
    
    assert expected == observed