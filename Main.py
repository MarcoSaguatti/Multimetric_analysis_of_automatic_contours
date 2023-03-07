import argparse
import sys
import os

import pandas as pd

import HD_DSC


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
    parser.add_argument(dest="new_config_path",
                        metavar="new_config_path",
                        default=None,
                        help=("""Path to the json file where the updated
                              configuration data will be saved"""
                              )
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
    new_folder_path = HD_DSC.check_new_folder_path(args.new_folder_path)
        
    # Convert to python path style.
    input_folder_path = args.input_folder_path.replace("\\", "/")
    config_path = args.config_path.replace("\\", "/")
    new_config_path = args.new_config_path.replace("\\", "/")
    excel_path = args.excel_path.replace("\\", "/")
    
    # If true new data will be concatenated with old ones.
    join_data = args.join_data    
    
    # Opening the json file where the lists of names are stored.
    config = HD_DSC.read_config(config_path)
    
    # List where final data will be stored.
    final_data = []
    
    # Input folder can not be empty.
    HD_DSC.exit_if_empty(input_folder_path)
    
    # Input folder must contain patient folders, not directly .dcm files.
    patient_folders = HD_DSC.store_patients(input_folder_path)   
    HD_DSC.exit_if_no_patients(input_folder_path,
                               patient_folders,
                               )
    # If join_data is True, old data will be extracted from excel_path,
    # otherwise the old excel file will be overwritten.
    if join_data:
        old_data = HD_DSC.load_existing_dataframe(excel_path)
        
        for patient_folder in patient_folders:
            patient_folder_path = os.path.join(input_folder_path,
                                               patient_folder,
                                               )
            
            # Patient folder can not be empty.
            HD_DSC.exit_if_empty(patient_folder_path)
            
            # RTSTRUCT and CT series should be in different folders.
            # Creating RTSTRUCT folder if it is not already present, otherwise
            # going on with the execution.
            rtstruct_folder_path = HD_DSC.create_folder(patient_folder_path,
                                                        "RTSTRUCT",
                                                        )
            
            # Creating CT folder if it is not already present, otherwise
            # going on with the execution.
            ct_folder_path = HD_DSC.create_folder(patient_folder_path,
                                                  "CT",
                                                  )
            
            # Filling CT and RTSTRUCT folders if both empty
            HD_DSC.fill_ct_rtstruct_folders(patient_folder_path,
                                            ct_folder_path,
                                            rtstruct_folder_path,
                                            )
            
            # If RTSTRUCT or CT folders are still empty there are no data.
            HD_DSC.exit_if_empty(rtstruct_folder_path)
            HD_DSC.exit_if_empty(ct_folder_path)
            
            # Extracting rtstruct file path.
            rtstruct_file_path = HD_DSC.extract_rtstruct_file_path(rtstruct_folder_path)
                
            # Extraction of patient ID and frame of reference UID.
            patient_id = HD_DSC.patient_info(rtstruct_file_path,
                                             "PatientID",
                                             )
            frame_of_reference_uid = HD_DSC.patient_info(rtstruct_file_path,
                                                         "FrameOfReferenceUID",
                                                         )
            
            print(f"Starting patient {patient_id} analysis")
            
            # If the current frame of reference is already in the excel file
            # we can move to the next one.
            try:
                frame_uid_in_old_data = HD_DSC.check_study(old_data,
                                                           frame_of_reference_uid,
                                                           patient_id,
                                                           )
                if frame_uid_in_old_data:
                    # Moving patient folder to a different location if the
                    # destination folder does not exist it will be
                    # automatically created.
                    HD_DSC.move_patient_folder(new_folder_path,
                                               patient_folder_path,
                                               patient_folder,
                                               )
                    continue
            except KeyError:
                pass
                    
            # Creating the list of all segments of current patient.
            all_segments = HD_DSC.extract_all_segments(ct_folder_path,
                                                       rtstruct_file_path,
                                                       )
            
            # Creating manual segments list.
            print("Creating the list of manual segments")
            unknown_segments = HD_DSC.find_unknown_segments(all_segments,
                                                            config,
                                                            )
            HD_DSC.user_selection(unknown_segments,
                                  config,
                                  )
            manual_segments = HD_DSC.extract_manual_segments(all_segments,
                                                             config,
                                                             )
            
            # Computing HD, DSC and SDSC for every segment in manual and MBS
            # lists.
            final_data = HD_DSC.extract_hausdorff_dice(manual_segments,
                                                       config,
                                                       ct_folder_path,
                                                       rtstruct_file_path,
                                                       final_data,
                                                       )
            
            # Moving patient folder to a different location, if the destination
            # folder does not exist it will be automatically created.
            HD_DSC.move_patient_folder(new_folder_path,
                                       patient_folder_path,
                                       patient_folder,
                                       )

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
        
        # Concatenating old and new dataframes.
        new_data = HD_DSC.concatenate_data(old_data,
                                           new_data,
                                           )
        
        # Saving dataframe to excel.
        print("Saving data")
        new_data.to_excel(excel_path,
                          sheet_name="Data",
                          index=False,
                          )
        
        # Saving configuration data.
        HD_DSC.save_config_data(config,
                                new_config_path,
                                )
        
        print("Execution successfully ended")
    
    else:
        print(f"Excel file at {excel_path} will be overwritten if already",
              "present, otherwise it will be created.",
              )
        
        for patient_folder in patient_folders:
            patient_folder_path = os.path.join(input_folder_path,
                                               patient_folder,
                                               )
            
            # Patient folder can not be empty.
            HD_DSC.exit_if_empty(patient_folder_path)
            
            # RTSTRUCT and CT series should be in different folders.
            # Creating RTSTRUCT folder if it is not already present, otherwise
            # going on with the execution.
            rtstruct_folder_path = HD_DSC.create_folder(patient_folder_path,
                                                        "RTSTRUCT",
                                                        )
            
            # Creating CT folder if it is not already present, otherwise
            # going on with the execution.
            ct_folder_path = HD_DSC.create_folder(patient_folder_path,
                                                  "CT",
                                                  )
            
            # Filling CT and RTSTRUCT folders if both empty
            HD_DSC.fill_ct_rtstruct_folders(patient_folder_path,
                                            ct_folder_path,
                                            rtstruct_folder_path,
                                            )
            
            # If RTSTRUCT or CT folders are still empty there are no data.
            HD_DSC.exit_if_empty(rtstruct_folder_path)
            HD_DSC.exit_if_empty(ct_folder_path)
            
            # Extracting rtstruct file path.
            rtstruct_file_path = HD_DSC.extract_rtstruct_file_path(rtstruct_folder_path)
                
            # Extraction of patient ID and frame of reference UID.
            patient_id = HD_DSC.patient_info(rtstruct_file_path,
                                             "PatientID",
                                             )
            frame_of_reference_uid = HD_DSC.patient_info(rtstruct_file_path,
                                                         "FrameOfReferenceUID",
                                                         )
            
            print(f"Starting patient {patient_id} analysis")
        
            # Creating the list of all segments of current patient.
            all_segments = HD_DSC.extract_all_segments(ct_folder_path,
                                                       rtstruct_file_path,
                                                       )
            
            # Creating manual segments list.
            print("Creating the list of manual segments")
            unknown_segments = HD_DSC.find_unknown_segments(all_segments,
                                                            config,
                                                            )
            HD_DSC.user_selection(unknown_segments,
                                  config,
                                  )
            manual_segments = HD_DSC.extract_manual_segments(all_segments,
                                                             config,
                                                             )
            
            # Computing HD, DSC and SDSC for every segment in manual and MBS
            # lists.
            final_data = HD_DSC.extract_hausdorff_dice(manual_segments,
                                                       config,
                                                       ct_folder_path,
                                                       rtstruct_file_path,
                                                       final_data,
                                                       )
            
            # Moving patient folder to a different location, if the destination
            # folder does not exist it will be automatically created.
            HD_DSC.move_patient_folder(new_folder_path,
                                       patient_folder_path,
                                       patient_folder,
                                       )
    
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
        # Saving dataframe to excel.
        print("Saving data")
        new_data.to_excel(excel_path,
                          sheet_name="Data",
                          index=False,
                          )
     
        # Saving configuration data.
        HD_DSC.save_config_data(config,
                                new_config_path,
                                )
        
        print("Execution successfully ended")
    
    
if __name__ == "__main__":
    main(sys.argv[1:])