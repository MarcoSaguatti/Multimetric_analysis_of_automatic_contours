import argparse
import sys
import os
import shutil
import json

import numpy as np
import pandas as pd
import pytest

import pydicom
from rt_utils import RTStructBuilder
import surface_distance as sd

import Hausdorff_Dice

# FIXME non va
# config_path = r"C:\Users\Marco\Desktop\università\Magistrale\software_and_computing\tests.json"
# # Opening the json file where the lists of names are stored.
# fd = open(config_path)
# config = json.load(fd)


#TODO trova un modo migliore
empty_folder = r"C:\Users\Marco\Desktop\università\Magistrale\software_and_computing\tests\test_is_empty\empty_folder"
non_empty_folder = r"C:\Users\Marco\Desktop\università\Magistrale\software_and_computing\tests\test_is_empty\non_empty_folder"

def test_is_empty_with_empty_folder():
    """
    This method checks if the function is_empty returns 1 when an empty folder
    is given as parameter.

    Returns
    -------
    None.

    """
    assert Hausdorff_Dice.is_empty(empty_folder) == 1
    
def test_is_empty_with_non_empty_folder():
    """
    This method checks if the function is_empty returns 0 when a non empty
    folder is given as parameter.

    Returns
    -------
    None.

    """
    assert Hausdorff_Dice.is_empty(non_empty_folder) == 0