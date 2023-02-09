import argparse
import sys
import os
import shutil
import json
import tempfile

import numpy as np
import pandas as pd
import pytest

import pydicom
from rt_utils import RTStructBuilder
import surface_distance as sd

import Hausdorff_Dice


# # Path to tests\test_voxel_spacing\CT
# ct_folder_path = r"Path\to\tests\test_voxel_spacing\CT"
# # Path to configuration file
# config_path = r"Path\to\config.json"
# # Path to tests\test_hausdorff_dice\input_folder
# input_folder = r"Path\to\tests\test_hausdorff_dice\input_folder"
# # Path to test.xlsx (if not there it will be created)
# excel_path = r"Path\to\tests\test_hausdorff_dice\test.xlsx"
# # Path to tests\test_hausdorff_dice\new_folder
# new_folder_path = r"Path\to\tests\test_hausdorff_dice\new_folder"

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
    
    expected = "1.3.6.1.4.1.14519.5.2.1.7085.2036.235949374640197733305184528698"
    observed = Hausdorff_Dice.patient_info(rtstruct_file_path,
                                           "FrameOfReferenceUID",
                                           )
    assert expected == observed
    
def test_compute_voxel_spacing():
    """
    GIVEN: the path to the folder containing a CT serie
        
    WHEN: running the function compute_voxel_spacing
        
    THEN: return the correct voxel spacing

    """
    # Path to CT serie folder
    ct_folder_path = r".\tests\test_compute_voxel_spacing\CT"
    
    expected = [1.0, 1.0, 3.0]
    observed = Hausdorff_Dice.compute_voxel_spacing(ct_folder_path)
    assert expected == observed  
    
# def test_voxel_spacing_has_three_elements():
#     """
#     This test checks that the function voxel_spacing returns a list of three
#     elements.

#     Returns
#     -------
#     None.

#     """
#     assert len(Hausdorff_Dice.voxel_spacing(ct_folder_path)) == 3

# def test_extract_manual_segments_has_five_elements():
#     """
#     This test checks that the function voxel_spacing returns a list of five
#     elements.

#     Returns
#     -------
#     None.

#     """
#     patient_data = RTStructBuilder.create_from(ct_folder_path, 
#                                                 rtstruct_file_path,
#                                                 )
#     alias_names = ["Prostate",
#                     "Rectum",
#                     "Bladder",
#                     "Femoral head (left)",
#                     "Femoral head right",
#                     ]
#     mbs_segments = ["Prostate_MBS",
#                     "Rectum_MBS",
#                     "Bladder_MBS",
#                     "FemoralHead (Left)_MBS",
#                     "FemoralHead (Right)_MBS",
#                     ]
#     dl_segments = ["Prostate_DL",
#                     "Anorectum_DL",
#                     "Bladder_DL",
#                     "Femur_Head_L_DL",
#                     "Femur_Head_R_DL",
#                     ]
#     fd = open(config_path)
#     config = json.load(fd)
    
#     manual_segments = Hausdorff_Dice.extract_manual_segments(patient_data,
#                                                               alias_names,
#                                                               mbs_segments,
#                                                               dl_segments,
#                                                               config,
#                                                               )
#     assert len(manual_segments) == 5
    
# def test_compute_metrics_returns_float():
#     """
#     This funtion checks that the three values returned by compute_metrics are
#     all of type float.

#     Returns
#     -------
#     None.

#     """
#     patient_data = RTStructBuilder.create_from(ct_folder_path, 
#                                                 rtstruct_file_path,
#                                                 )
#     reference_segment = "Bladder_MBS"
#     segment_to_compare = "Bladder_DL"
#     voxel_spacing_mm = [1, 1, 3]
#     sdsc, dsc, hd = Hausdorff_Dice.compute_metrics(patient_data,
#                                                     reference_segment,
#                                                     segment_to_compare,
#                                                     voxel_spacing_mm,
#                                                     )
#     assert type(sdsc) == np.float64
#     assert type(dsc) == np.float64
#     assert type(sdsc) == np.float64
    
# def test_hausdorff_dice():
#     """
#     This function checks if the length of the dataframe after running the
#     function hausdorff_dice for one patient is 15 as expected.

#     Returns
#     -------
#     None.

#     """
#     Hausdorff_Dice.hausdorff_dice(input_folder,
#                                   config_path,
#                                   excel_path,
#                                   new_folder_path,
#                                   join_data = False,
#                                   )
#     dataframe = pd.read_excel(excel_path)
#     assert len(dataframe) == 15
    