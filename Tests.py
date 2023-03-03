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
    non_empty_folder = r".\tests\test_patient"
    
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
    rtstruct_file_path = r".\tests\test_patient\RTSTRUCT\RS_002.dcm"
    
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
    rtstruct_file_path = r".\tests\test_patient\RTSTRUCT\RS_002.dcm"
    
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
    ct_folder_path = r".\tests\test_patient\CT"
    
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
    ct_folder_path = r".\tests\test_patient\CT"
    
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
    ct_folder_path = r".\tests\test_patient\CT"
    
    # Path to RTSTRUCT file
    rtstruct_file_path = r".\tests\test_patient\RTSTRUCT\RS_002.dcm"
    
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
    config_path = r".\tests\config.json"
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
    config_path = r".\tests\config.json"
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
    ct_folder_path = r".\tests\test_patient\CT"
    rtstruct_file_path = r".\tests\test_patient\RTSTRUCT\RS_002.dcm"
    
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
    parent_folder_path = r".\tests\test_patient"
    
    expected = r".\tests\test_patient\CT"
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
    
def test_check_new_folder_path():
    """
    GIVEN: the path to a folder
        
    WHEN: running the function check_new_folder_path
        
    THEN: return the path to the folder in python style

    """
    # Path to a folder
    folder_path = r".\tests\test_patient"
    
    expected = r"./tests/test_patient"
    observed = Hausdorff_Dice.check_new_folder_path(folder_path)
    
    assert expected == observed
    
def test_check_new_folder_path_without_folder():
    """
    GIVEN: the default value of new_folder_path
        
    WHEN: running the function check_new_folder_path
        
    THEN: return False

    """
    # Default value of new_folder_path
    folder_path = "."
    
    expected = False
    observed = Hausdorff_Dice.check_new_folder_path(folder_path)
    
    assert expected == observed
    
def test_read_config():
    """
    GIVEN: the path to a json file
        
    WHEN: running the function read_config
        
    THEN: return the data inside the file

    """
    # Path to the configuration file
    config_path = r".\tests\test.json"
    
    expected = {"External names" : ["External"]}
    observed = Hausdorff_Dice.read_config(config_path)
    
    assert expected == observed
    
def test_extract_rtstruct_file_path():
    """
    GIVEN: the path to the folder containing the RTSTRUCT file
        
    WHEN: running the function extract_rtstruct_file_path
        
    THEN: return the path to the RTSTRUCT file

    """
    # Path to the rtstruct folder
    rtstruct_folder_path = r".\tests\test_extract_rtstruct_file_path"
    
    expected = r".\tests\test_extract_rtstruct_file_path\RS_002.dcm"
    observed = Hausdorff_Dice.extract_rtstruct_file_path(rtstruct_folder_path)
    
    assert expected == observed
    
def test_create_segments_matrices():
    """
    GIVEN: a list of manual segments and a configuration file
        
    WHEN: running the function create_segments_matrices
        
    THEN: return the matrix of reference segments and the matrix of segments
          to compare

    """
    # List of manual segments names
    manual_seg = ["Prostata",
                  "Retto",
                  "Vescica",
                  "FemoreSinistro",
                  "FemoreDestro",
                  ]
    
    # Loading configuration file
    config_path = r".\tests\test_extract_manual_segments\config.json"
    config = Hausdorff_Dice.read_config(config_path)
    
    expected_ref = [["Prostata",
                     "Retto",
                     "Vescica",
                     "FemoreSinistro",
                     "FemoreDestro",
                     ],
                    ["Prostata",
                     "Retto",
                     "Vescica",
                     "FemoreSinistro",
                     "FemoreDestro",
                     ],
                    ["Prostate_MBS",
                     "Rectum_MBS",
                     "Bladder_MBS",
                     "FemoralHead (Left)_MBS",
                     "FemoralHead (Right)_MBS",
                     ],
                    ]
    expected_comp = [["Prostate_MBS",
                      "Rectum_MBS",
                      "Bladder_MBS",
                      "FemoralHead (Left)_MBS",
                      "FemoralHead (Right)_MBS",
                      ],
                     ["Prostate_DL",
                      "Anorectum_DL",
                      "Bladder_DL",
                      "Femur_Head_L_DL",
                      "Femur_Head_R_DL",
                      ],
                     ["Prostate_DL",
                      "Anorectum_DL",
                      "Bladder_DL",
                      "Femur_Head_L_DL",
                      "Femur_Head_R_DL",
                      ],
                     ]
    obs_ref, obs_comp = Hausdorff_Dice.create_segments_matrices(manual_seg,
                                                                config,
                                                                )
    
    assert expected_ref == obs_ref
    assert expected_comp == obs_comp
    
def test_extract_hausdorff_dice():
    """
    GIVEN: the list of manual segments, the configuration file, the path to
           the CT folder, the path to the RTSTRUCT file and the list
           final_data
        
    WHEN: running the function extract_hausdorff_dice
        
    THEN: return the correct list of data

    """
    # List of manual segments names
    manual_seg = ["Prostata",
                  "Retto",
                  "Vescica",
                  "FemoreSinistro",
                  "FemoreDestro",
                  ]
    
    # Loading configuration file
    config_path = r".\tests\test_extract_manual_segments\config.json"
    config = Hausdorff_Dice.read_config(config_path)
    
    # CT folder path
    ct = r".\tests\test_extract_hausdorff_dice\CT"
    
    # RTSTRUCT file path
    rs = r".\tests\test_extract_hausdorff_dice\RTSTRUCT\RS_002.dcm"
    
    # List where data will be stored
    final_data = []
    
    expected_2_3 = "Vescica"
    expected_5_6 = 9
    expected_13_2 = "MBS-DL"
    observed = Hausdorff_Dice.extract_hausdorff_dice(manual_seg,
                                                     config,
                                                     ct,
                                                     rs,
                                                     final_data,
                                                     )
    
    assert expected_2_3 == observed[2][3]
    assert math.isclose(expected_5_6, observed[5][6])
    assert expected_13_2 == observed[13][2]
    
def test_load_existing_dataframe():
    """
    GIVEN: the path to an existing excel file
        
    WHEN: running the function load_existing_dataframe
        
    THEN: return the content of the excel file

    """
    # Path to existing excel file
    excel_path = r".\tests\test_load_existing_dataframe\test_dataframe.xlsx"
    
    expected_d = {"Patient ID": ["Pelvic-Ref-002"],
                  "Alias name": ["Prostate"],
                  "Frame of reference": [8],
                  }
    expected = pd.DataFrame(data=expected_d)
    observed = Hausdorff_Dice.load_existing_dataframe(excel_path)
    
    assert expected.equals(observed)
    
def test_load_existing_dataframe_with_no_excel():
    """
    GIVEN: the path to a non existing excel file
        
    WHEN: running the function load_existing_dataframe
        
    THEN: an empty dataframe is returned

    """
    # Create a temporary empty folder
    temp_folder = tempfile.TemporaryDirectory()
    excel_path = temp_folder.name+"non_existing_excel.xlsx"
    
    expected = pd.DataFrame()
    observed = Hausdorff_Dice.load_existing_dataframe(excel_path)
    
    assert expected.equals(observed)
        
def test_concatenate_data():
    """
    GIVEN: two pandas dataframes
        
    WHEN: concatenating them with the function concatenate_data
        
    THEN: obtaining the correct dataframe

    """
    # Path to existing excel file
    excel_path = r".\tests\test_load_existing_dataframe\test_dataframe.xlsx"
    
    old_data = Hausdorff_Dice.load_existing_dataframe(excel_path)
    d = {"Patient ID": ["Pelvic-Ref-003"],
         "Alias name": ["Bladder"],
         "Frame of reference": [5],
         }
    new_data = pd.DataFrame(data=d)
    
    expected_d = {"Patient ID": ["Pelvic-Ref-002","Pelvic-Ref-003"],
                  "Alias name": ["Prostate","Bladder"],
                  "Frame of reference": [8,5],
                  }
    expected = pd.DataFrame(data=expected_d)
    observed = Hausdorff_Dice.concatenate_data(old_data,
                                               new_data,
                                               )
    
    assert expected.equals(observed)
    
def test_check_study():
    """
    GIVEN: A dataframe, a frame of reference uid in the dataframe, a frame of
           reference uid not in the dataframe and the patient id
        
    WHEN: running the function check_study
        
    THEN: it is returned True for the frame of reference uid that is in the
          dataframe, while it is returned False for the frame of reference
          uid not in the dataframe

    """
    # Path to existing excel file
    excel_path = r".\tests\test_load_existing_dataframe\test_dataframe.xlsx"
    
    old_data = Hausdorff_Dice.load_existing_dataframe(excel_path)
    correct_frame_of_reference = 8
    wrong_frame_of_reference = 55
    patient_id = "Pelvic-Ref-002"
    
    correct_expected = True
    correct_observed = Hausdorff_Dice.check_study(old_data,
                                                  correct_frame_of_reference,
                                                  patient_id,
                                                  )
    wrong_expected = False
    wrong_observed = Hausdorff_Dice.check_study(old_data,
                                                wrong_frame_of_reference,
                                                patient_id,
                                                )
    
    assert correct_expected == correct_observed
    assert wrong_expected == wrong_observed
    
def test_exit_if_empty():
    """
    GIVEN: an empty folder path
        
    WHEN: running the function exit_if_empty
        
    THEN: raises SystemExit

    """
    # Create a temporary empty folder
    temp_empty_folder = tempfile.TemporaryDirectory()
    
    with pytest.raises(SystemExit):
        Hausdorff_Dice.exit_if_empty(temp_empty_folder.name)
        
def test_exit_if_no_patients():
    """
    GIVEN: an empty patients list
        
    WHEN: running the function exit_if_no_patients
        
    THEN: raises SystemExit

    """
    # Create a temporary empty folder
    temp_empty_folder = tempfile.TemporaryDirectory()
    
    # Empty patient folders list
    patient_folders = []
    
    with pytest.raises(SystemExit):
        Hausdorff_Dice.exit_if_no_patients(temp_empty_folder.name,
                                           patient_folders,
                                           )
    