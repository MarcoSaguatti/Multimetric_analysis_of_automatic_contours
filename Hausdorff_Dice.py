# from __future__ import absolute_import, division, print_function

import argparse
import sys
import logging
import pandas as pd
import os
import shutil
import json

import pydicom
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
    # TODO use more prints to make the user know whats going on during
    # execution (then see if it is better to use print, log messages or other)
    # TODO printed messages must be checked and rewritten in the correct way
                     
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description 
                                     = "HD, volDSC and surfDSC computation")
    parser.add_argument("-i", "--input-folder",
                        dest="input_folder_path",
                        metavar="PATH",
                        default=None,
                        required=True,
                        help="Path to the folder of input DICOM study/ies",
                        )
    parser.add_argument("-c", "--config-path",
                        dest="config_path",
                        metavar="PATH",
                        default=None,
                        required=True,
                        help="Path to the configuration json file",
                        )
    parser.add_argument("-e", "--excel-path",
                        dest="excel_path",
                        metavar="PATH",
                        default=None,
                        required=True,
                        help="""Path to the .xlsx file (if not present it will
                             be automatically created
                             """,
                        )
    parser.add_argument("-n", "--new-folder",
                        dest="new_folder_path",
                        metavar="PATH",
                        default=False,
                        required=False,
                        help="""Path where patient folders will be moved after
                             execution (optional)
                             """,
                        )
    parser.add_argument("-j", "--join-data",
                        dest="join_data",
                        metavar=bool,
                        default=False,
                        required=False,
                        help="Join previously extracted data with new ones",
                        )
    
    args = parser.parse_args(argv)
        
    # TODO check if keep this or not
    # Check required arguments
    if args.input_folder_path == None:
        logging.warning("Please specify input DICOM study folder!")
    if args.config_path == None:
        logging.warning("Please specify where is the configuration file!")
    if args.excel_path == None:
        logging.warning("""Please specify the location of
                        .xlsx file where data will be stored
                        """,
                        )
     
    # Convert to python path style
    input_folder_path = args.input_folder_path.replace("\\", "/")
    new_folder_path = args.new_folder_path.replace("\\", "/")
    config_path = args.config_path.replace("\\", "/")
    excel_path = args.excel_path.replace("\\", "/")
    
    # If true new data will be concatenated with old ones
    join_data = args.join_data
    
    # Opening the json file where the lists of names are stored
    fd = open(config_path)
    config = json.load(fd)
    
    # Extracting compared segmentation methods, mbs, dl and alias segments
    # names.
    compared_methods = config["Compared methods"]
    mbs_segments = config["MBS segments"]
    dl_segments = config["DL segments"]
    alias_names = config["Alias names"]
    
    # List where final data will be stored.
    final_data = []
    
    # If join_data is True, old data will be extracted from excel_path,
    # otherwise the old excel file will be overwritten.
    if join_data:
        try:
            # loading existing data
            old_dataframe = pd.read_excel(excel_path)
            print(f"Successfully loaded {excel_path}")
        except:
            # TODO check if it is correct to use print
            print(f"Failed to load {excel_path}, a new file will be created")
    else:
        print(f"""Excel file at {excel_path} will be overwritten if already
              present, otherwise it will be created.""")
    
    # Check that input folder is not empty
    if len(os.listdir(input_folder_path)) == 0:
        sys.exit(f"{input_folder_path} is empty, aborting execution")
    
    # Check that input folder contains patient folders
    patient_folders = []
    for folder in os.listdir(input_folder_path):
        # Only patient folders are needed, other files are skipped
        if not os.path.isfile(os.path.join(input_folder_path,folder)):
            patient_folders.append(folder)
    if len(patient_folders) == 0:
        sys.exit(f"""{input_folder_path} does not contain folders.
                 Be sure to provide as input the folder that contains the
                 patients and not directly dcm files.
                 Aborting execution
                 """,
                 )
    
    # Selecting one patient at the time and analyzing it
    for patient_folder in patient_folders:
        patient_folder_path = os.path.join(input_folder_path,
                                           patient_folder,
                                           )
        
        # Checking that patient folder is not empty
        if len(os.listdir(patient_folder_path)) == 0:
            sys.exit(f"{patient_folder_path} is empty, aborting execution")
        
        # RTSTRUCT and DICOM series should be in different folders.
        # Creating RTSTRUCT folder if it is not already present, otherwise
        # going on with execution.
        rtstruct_folder = "RTSTRUCT"
        rtstruct_folder_path = os.path.join(patient_folder_path,
                                            rtstruct_folder,
                                            )
        try:
            os.mkdir(rtstruct_folder_path)
        except FileExistsError:
            pass
        
        # Creating CT folder if it is not already present, otherwise
        # going on with execution
        dicom_series_folder = "CT"
        dicom_series_folder_path = os.path.join(patient_folder_path,
                                                dicom_series_folder,
                                                )
        try:
            os.mkdir(dicom_series_folder_path)
        except FileExistsError:
            pass
        
        # Filling CT and RTSTRUCT folder if both empty
        rtstruct_folder_is_empty = (len(os.listdir(rtstruct_folder_path))==0)
        dicom_folder_is_empty = (len(os.listdir(dicom_series_folder_path))==0)
        if (rtstruct_folder_is_empty and dicom_folder_is_empty):
            print("""Moving CT.dcm files into CT folder and RS.dcm files into
                  RTSTRUCT folder""")
            for file in os.listdir(patient_folder_path):
                file_path = os.path.join(patient_folder_path,
                                         file,
                                         )
                # TODO should be more general (maybe looking at the metadata)
                if os.path.isfile(file_path):
                    if file.startswith("CT"):
                        shutil.move(file_path,
                                    dicom_series_folder_path,
                                    )
                    elif file.startswith("RS"):
                        shutil.move(file_path,
                                    rtstruct_folder_path,
                                    )  
                    else:
                        pass
                else:
                    pass
        # Exit to not mix different data
        elif rtstruct_folder_is_empty:
            sys.exit("""Only RTSTRUCT folder is empty. Aborting execution
                     to not mix different data. Check the data and try
                     again""")
        # Exit to not mix different data
        elif dicom_folder_is_empty:
            sys.exit("""Only CT folder is empty. Aborting execution to not
                     mix different data. Check the data and try again""")
        # Going on if both folders have already data inside, to not merge
        # different data
        else:
            print("""Both RTSTRUCT and CT folders have already files in them.
                  Thus, no files will be moved""")
            pass
        
        # Check if RTSTRUCT or CT folders are still empty
        rtstruct_folder_is_empty = (len(os.listdir(rtstruct_folder_path))==0)
        dicom_folder_is_empty = (len(os.listdir(dicom_series_folder_path))==0)
        if (rtstruct_folder_is_empty or dicom_folder_is_empty):
            sys.exit("""CT.dcm and/or RS.dcm files not available. Aborting
                     execution. Check the data and try again""")
        
        # Extracting rtstruct file path
        for file in os.listdir(rtstruct_folder_path):
            rtstruct_file_path = os.path.join(rtstruct_folder_path,
                                                     file,
                                                     )
            
        # TODO check if it is a good position and if it must be put in a
        # function.
        # Extraction of patient ID and frame of reference UID
        rtstruct_dataset = pydicom.dcmread(rtstruct_file_path)
        patient_id = rtstruct_dataset["PatientID"].value
        frame_of_reference_uid = rtstruct_dataset["FrameOfReferenceUID"].value
        
        # TODO use better names. How do I have to manage folders of patient
        # already done? Is there a better way to write this?
        # If join_data is True we need to check if the current study is
        # already in the dataframe and if it is to skip it. Otherwise no
        # checks are needed and every study will be analyzed.
        if join_data:
            try:
                for frame_of_reference in old_dataframe.loc[:,"Frame of reference"]:
                    if frame_of_reference == frame_of_reference_uid:
                        print("""This study is alreday in the dataframe, going
                              to the next one
                              """,
                              )
                        frame_uid_in_old_data = True
                        break
                    else:
                        frame_uid_in_old_data = False
                if frame_uid_in_old_data:
                    continue
            except NameError:
                pass
                        
        # TODO check if the names are good or must be changed, put this in a
        # function, and check if it is ok to keep it here.
        # Extracting voxel spacing
        ct_images = os.listdir(dicom_series_folder_path)
        slices =[pydicom.read_file(dicom_series_folder_path+"/"+s, force=True) for s in ct_images]
        slices = sorted(slices, key=lambda x:x.ImagePositionPatient[2])
        pixel_spacing_mm = list(map(float, slices[0].PixelSpacing._list))
        slice_thickness_mm = float(slices[0].SliceThickness)
        voxel_spacing_mm = pixel_spacing_mm.copy()
        voxel_spacing_mm.append(slice_thickness_mm)
        print("voxel spacing (mm):",voxel_spacing_mm)
            
        # Reading current patient files
        patient_data = RTStructBuilder.create_from(dicom_series_folder_path, 
                                               rtstruct_file_path,
                                               )
        
        # TODO put some code to handle the case in which one or more of the
        # OARs is not present.
        # Creates the list of manual segments
        all_segments = patient_data.get_roi_names()
        manual_segments = [0 for i in range(len(alias_names))]
        for name in all_segments:
            if name in mbs_segments:
                continue
            elif name in dl_segments:
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
                to_keep = input(f"Do you want to keep {name}? Enter Y (yes) or N (no) \n").upper()
                # TODO put some code to handle the case in which the user
                # provides the wrong input, and see if there is a better way
                # to write the following if-else.
                if to_keep == "Y":
                    # TODO check if it is correct to print on the standard
                    # output, if it coorect how I wrote the code and put some
                    # check to the input provided by the user.
                    what_is = input(f"To which alias name is {name} associated? Enter P (Prostate), A (Anorectum), B (Bladder), L (Left femur) or R (Right femur) \n").upper()
                    if what_is == "P":
                        manual_segments[0] = name
                        config["Prostate names"].append(name)
                        print(name,"added to Prostate names in config.json")
                    elif what_is == "A":
                        manual_segments[1] = name
                        config["Rectum names"].append(name)
                        print(name,"added to Rectum names in config.json")
                    elif what_is == "B":
                        manual_segments[2] = name
                        config["Bladder names"].append(name)
                        print(name,"added to Bladder names in config.json")
                    elif what_is == "L":
                        manual_segments[3] = name
                        config["Left femur names"].append(name)
                        print(name,"added to Left femur names in config.json")
                    elif what_is == "R":
                        manual_segments[4] = name
                        config["Right femur names"].append(name)
                        print(name,"added to Right femur names in config.json")
                elif to_keep == "N":
                    continue
        
        # With these lists it is possible to use a for loop to perform
        # manual-MBS, manual-DL and MBS-DL comparisons.
        reference_segments = [manual_segments, manual_segments, mbs_segments]
        to_compare_segments = [mbs_segments, dl_segments, dl_segments]
        
        # TODO should be subdivided into functions.
        # Computing HD, DSC and SDSC for every segment in manual and MBS lists.
        for compared_methods_index in range(len(compared_methods)):
            # TODO maybe print some message to let the user know what's going
            # on and extract here values to store that are not segment
            # dependent, and clean the code.
            
            
            for segment_index in range(len(alias_names)):
                # TODO all this part must be rewritten with correct rows
                # length.
                
                # TODO automatic extraction of the contour is needed
                # Binary labelmap creation
                reference_segment_labelmap = patient_data.get_roi_mask_by_name(reference_segments[compared_methods_index][segment_index])
                segment_to_compare_labelmap = patient_data.get_roi_mask_by_name(to_compare_segments[compared_methods_index][segment_index])
                
                # TODO shorten names
                # Metrics computation
                surf_dists = surface_distance.compute_surface_distances(reference_segment_labelmap,
                                                                        segment_to_compare_labelmap,
                                                                        voxel_spacing_mm,
                                                                        )
                
                surface_dice = surface_distance.compute_surface_dice_at_tolerance(surf_dists,
                                                                                  tolerance_mm=3,
                                                                                  )
                #print(patient_folder,alias_names[segment_index],compared_methods[compared_methods_index],"surface Dice:",surface_dice)
                
                volume_dice = surface_distance.compute_dice_coefficient(reference_segment_labelmap,
                                                                        segment_to_compare_labelmap,
                                                                        )
                #print(patient_folder,alias_names[segment_index],compared_methods[compared_methods_index],"volumetric Dice:",volume_dice)
                
                
                hausdorff_distance = surface_distance.compute_robust_hausdorff(surf_dists,
                                                                               percent=95,
                                                                               )
                #print(patient_folder,alias_names[segment_index],compared_methods[compared_methods_index],"95% Hausdorff distance:",hausdorff_distance,"mm")
                
                # Creating a temporary list to store the current row of the
                # final dataframe.
                row_data = [patient_id,
                            frame_of_reference_uid,
                            compared_methods[compared_methods_index],
                            reference_segments[compared_methods_index][segment_index],
                            to_compare_segments[compared_methods_index][segment_index],
                            alias_names[segment_index],
                            hausdorff_distance,
                            volume_dice,
                            surface_dice,
                            ]
                
                # Adding the constructed raw to final_data
                final_data.append(row_data)
      
        # TODO check if this indentation can be acceptable
        # Moving patient folder to a different location, if the destination
        # folder does not exist it will be automatically created.
        if new_folder_path:
            shutil.move(patient_folder_path,
                        os.path.join(new_folder_path, patient_folder),
                        )
            #TODO this should not be a print and should be shorter
            print(f"{patient_folder} successfully moved to {new_folder_path}")
        else:
            pass
        
    # Creating the dataframe
    new_dataframe = pd.DataFrame(final_data,
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
            # Concatenating old and new datagrames
            frames = [old_dataframe, new_dataframe]
            new_dataframe = pd.concat(frames, ignore_index=True)
            print("Old and new dataframe concatenated")
        except NameError:
            print("""There is not an old dataframe, concatenation not
                  performed""")
            # pass
        
    
    # Saving dataframe to excel
    new_dataframe.to_excel(excel_path, sheet_name="Data", index=False)
     
    # TODO check if it is better to change names
    # Updating config.json
    json_object = json.dumps(config, indent=4)
    with open(config_path, "w") as outfile:
        outfile.write(json_object)
    
    # with open(r"C:\Users\Marco\Documents\tirocinio\scripting_3DSlicer\config.json", "w") as outfile:
    #     outfile.write(json_object)
        
                     

if __name__ == "__main__":
    main(sys.argv[1:])