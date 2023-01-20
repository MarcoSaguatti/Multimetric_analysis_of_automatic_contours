# from __future__ import absolute_import, division, print_function

import argparse
import sys
import logging
import pandas as pd
import os
import shutil

from rt_utils import RTStructBuilder
import surface_distance

def move_file_folder():
    return

# TODO Check if it is correct to put a docstring after main and if I have to
# add Parameters and other stuff (initially this was in logging.info).
# TODO check if it is better to use logging messages or not (and how to 
# visualize them)
def main(argv):
    """Computation of Hausdorff distance (HD), volumetric Dice similarity 
    coefficient (volDSC) and surface Dice similarity coefficient (surfDSC) 
    between manual and automatic segmentations for pelvic structures.
    
    """
    # TODO Create the backbone of the script (open the dcm files), then add 
    #one new small piece at the time
                     
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description 
                                     = "HD, volDSC and surfDSC computation")
    parser.add_argument("-i", "--input-folder",
                        dest="input_folder",
                        metavar="PATH",
                        default=None,
                        required=True,
                        help="Path to the folder of input DICOM study/ies",
                        )
    
    args = parser.parse_args(argv)
        
    # Check required arguments
    if args.input_folder == None:
        logging.warning('Please specify input DICOM study folder!')
     
    # Convert to python path style
    input_folder_path = args.input_folder.replace('\\', '/')
    
    # TODO put some checks and alternatives if input_folder is already
    # patient_folder and if input_folder contains files and not only dir.
    patient_folders = [folder for folder in os.listdir(input_folder_path)]
    for patient_folder in patient_folders:
        patient_folder_path = os.path.join(input_folder_path,
                                           patient_folder,
                                           )
        
        # TODO put some checks in case folders or incorrect files are present
        # and if folder structure is different.
        # RTSTRUCT and DICOM series should be in different folders
        rtstruct_folder = "RTSTRUCT"
        rtstruct_folder_path = os.path.join(patient_folder_path,
                                            rtstruct_folder,
                                            )
        os.mkdir(rtstruct_folder_path)
        dicom_series_folder = "DICOM"
        dicom_series_folder_path = os.path.join(patient_folder_path,
                                                dicom_series_folder,
                                                )
        os.mkdir(dicom_series_folder_path)
        for file in os.listdir(patient_folder_path):
            file_path = os.path.join(patient_folder_path,
                                     file,
                                     )
            if os.path.isfile(file_path):
                if file.startswith("CT"):
                   shutil.move(file_path,
                               dicom_series_folder_path,
                               )
                elif file.startswith("RS"):
                   shutil.move(file_path,
                               rtstruct_folder_path,
                               )
                   rtstruct_file_path = os.path.join(rtstruct_folder_path,
                                                     file,
                                                     )
                else:
                    pass
            else:
                pass
            
        # Reading current patient files
        rtstruct = RTStructBuilder.create_from(dicom_series_folder_path, 
                                               rtstruct_file_path,
                                               )
        
        # TODO automatic extraction of the contour is needed
        # Binary labelmap creation
        reference_segment_labelmap = rtstruct.get_roi_mask_by_name("Vescica")
        segment_to_compare_labelmap = rtstruct.get_roi_mask_by_name("Bladder_MBS")
        
        # TODO must be extracted from images, and see if it is better to put
        # it in another part of the code.
        voxel_spacing_mm = [0.977, 0.977, 3]
        
        # TODO shorten names
        # Metrics computation
        surf_dists = surface_distance.compute_surface_distances(reference_segment_labelmap,
                                                                segment_to_compare_labelmap,
                                                                voxel_spacing_mm,
                                                                )
        surface_dice = surface_distance.compute_surface_dice_at_tolerance(surf_dists,
                                                                          tolerance_mm=3,
                                                                          )
        print("Surface Dice:",surface_dice)
        hausdorff_distance = surface_distance.compute_robust_hausdorff(surf_dists,
                                                                       percent=95,
                                                                       )
        print("95% Hausdorff distance:",hausdorff_distance,"mm")
        volume_dice = surface_distance.compute_dice_coefficient(reference_segment_labelmap,
                                                                segment_to_compare_labelmap,
                                                                )
        print("Volumetric Dice:",volume_dice)
        
                     

if __name__ == "__main__":
    main(sys.argv[1:])