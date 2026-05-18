#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standalone descriptor_generator_2 script.

Usage (example):
    python descriptor_generator.py --name "MOF001" \
                                   --structure "path/to/MOF001.cif" \
                                   --prediction_type "water" \
                                   --session_id "1234"

You can also import the function descriptor_generator_2 into another script.
"""

import os
import shutil
import subprocess
import numpy as np
import pandas as pd
import argparse

# --------------------------------------------------------------------------------------
# 1) CONFIGURATION & PLACEHOLDERS
# --------------------------------------------------------------------------------------

# You might want to set this to the path on your machine where MOFSIMPLIFY is located.
MOFSIMPLIFY_PATH = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Fingerprinting_tests/"  # Update this path



# This function is called in your code; if it’s part of MOFSIMPLIFY,
# either import it directly or replicate its behavior here.
def get_primitive(input_cif, output_cif):
    """
    Placeholder for the get_primitive() function.
    Replace this with the actual implementation or import from MOFSIMPLIFY.
    """
    # For now, we’ll just pretend we wrote a file successfully.
    # In reality, you'd call the actual function here.
    if not os.path.exists(input_cif):
        raise ValueError("Input CIF does not exist.")
    # e.g., do something to generate `output_cif`.
    with open(output_cif, 'w') as f:
        f.write("Primitive CIF content here.")
    return


# --------------------------------------------------------------------------------------
# 2) THE MAIN FUNCTION
# --------------------------------------------------------------------------------------

def descriptor_generator_2(name, structure, prediction_type, session_id="1234"):
    """
    descriptor_generator_2 is used to generate RACs and Zeo++ descriptors.
    
    :param name:           str, the name of the MOF being analyzed.
    :param structure:      str, the text content of the CIF file of the MOF being analyzed.
    :param prediction_type: str, indicates the type of prediction (e.g., "water" or "acid").
    :param session_id:      str, ID for session handling (defaults to "1234" if not provided).
    :return: str, 'FAILED' if descriptor generation fails, otherwise 'SUCCESS'.
    """ 
    # Build paths (assumes MOFSIMPLIFY_PATH is globally defined in this file).
    temp_file_folder = MOFSIMPLIFY_PATH + "temp_file_creation_" + session_id + '/'
    cif_folder = os.path.join(temp_file_folder, 'cifs/')

    # Ensure these folders exist (or handle if they don’t).
    os.makedirs(cif_folder, exist_ok=True)

    # Write out the CIF file.
    cif_file_path = os.path.join(cif_folder, f"{name}.cif")
    try:
        with open(cif_file_path, 'w') as cif_file:
            cif_file.write(structure)
    except FileNotFoundError:
        return 'FAILED'

    # Create output folders for RACs & Zeo++
    feature_generation_folder = os.path.join(temp_file_folder, 'feature_generation')
    os.makedirs(feature_generation_folder, exist_ok=True)
    
    RACs_folder = os.path.join(feature_generation_folder, f"{prediction_type}_RACs")
    zeo_folder  = os.path.join(feature_generation_folder, f"{prediction_type}_zeo++")

    # Delete + recreate the folders to ensure a "fresh start"
    if os.path.exists(RACs_folder):
        shutil.rmtree(RACs_folder)
    os.mkdir(RACs_folder)

    if os.path.exists(zeo_folder):
        shutil.rmtree(zeo_folder)
    os.mkdir(zeo_folder)

    # Run get_primitive to generate a primitive CIF
    primitive_cif_path = os.path.join(cif_folder, f"{name}_primitive.cif")
    try:
        get_primitive(cif_file_path, primitive_cif_path)
    except ValueError:
        return 'FAILED'

    # Prepare the commands for Zeo++ calls and the RAC_getter script
    cmd1 = f"{MOFSIMPLIFY_PATH}zeo++-0.3/network -ha -res {zeo_folder}{name}_pd.txt {primitive_cif_path}"
    cmd2 = f"{MOFSIMPLIFY_PATH}zeo++-0.3/network -sa 1.4 1.4 10000 {zeo_folder}{name}_sa.txt {primitive_cif_path}"
    cmd3 = f"{MOFSIMPLIFY_PATH}zeo++-0.3/network -volpo 1.4 1.4 10000 {zeo_folder}{name}_pov.txt {primitive_cif_path}"
    cmd4 = f"python {MOFSIMPLIFY_PATH}model/RAC_getter.py {cif_folder} {name} {RACs_folder}"

    # Execute the commands in parallel
    process1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True)
    process2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
    process3 = subprocess.Popen(cmd3, stdout=subprocess.PIPE, shell=True)
    process4 = subprocess.Popen(cmd4, stdout=subprocess.PIPE, shell=True)

    # Wait for them to finish and capture outputs (if needed)
    output1, _ = process1.communicate()
    output2, _ = process2.communicate()
    output3, _ = process3.communicate()
    output4, _ = process4.communicate()

    # Check if all three Zeo++ files exist
    pd_path  = os.path.join(zeo_folder, f"{name}_pd.txt")
    sa_path  = os.path.join(zeo_folder, f"{name}_sa.txt")
    pov_path = os.path.join(zeo_folder, f"{name}_pov.txt")

    if not (os.path.exists(pd_path) and os.path.exists(sa_path) and os.path.exists(pov_path)):
        print("Not all 3 files exist, so at least one Zeo++ call failed!")
        return 'FAILED'

    # Initialize placeholders
    largest_included_sphere = np.nan
    largest_free_sphere = np.nan
    largest_included_sphere_along_free_sphere_path = np.nan
    unit_cell_volume = np.nan
    crystal_density = np.nan
    VSA = np.nan
    GSA = np.nan
    VPOV = np.nan
    GPOV = np.nan
    POAV = np.nan
    PONAV = np.nan
    GPOAV = np.nan
    GPONAV = np.nan
    POAV_volume_fraction = np.nan
    PONAV_volume_fraction = np.nan

    # Parse the pd.txt
    with open(pd_path) as f:
        pore_diameter_data = f.readlines()
        for row in pore_diameter_data:
            # largest included sphere, free sphere, included sphere along free sphere path
            largest_included_sphere = float(row.split()[1])
            largest_free_sphere = float(row.split()[2])
            largest_included_sphere_along_free_sphere_path = float(row.split()[3])

    # Parse the sa.txt
    with open(sa_path) as f:
        surface_area_data = f.readlines()
        for i, row in enumerate(surface_area_data):
            if i == 0:
                unit_cell_volume = float(row.split("Unitcell_volume:")[1].split()[0])
                crystal_density  = float(row.split("Density:")[1].split()[0])
                VSA = float(row.split("ASA_m^2/cm^3:")[1].split()[0])
                GSA = float(row.split("ASA_m^2/g:")[1].split()[0])

    # Parse the pov.txt
    with open(pov_path) as f:
        pore_volume_data = f.readlines()
        for i, row in enumerate(pore_volume_data):
            if i == 0:
                density = float(row.split("Density:")[1].split()[0])
                POAV = float(row.split("POAV_A^3:")[1].split()[0])
                PONAV = float(row.split("PONAV_A^3:")[1].split()[0])
                GPOAV = float(row.split("POAV_cm^3/g:")[1].split()[0])
                GPONAV = float(row.split("PONAV_cm^3/g:")[1].split()[0])
                POAV_volume_fraction  = float(row.split("POAV_Volume_fraction:")[1].split()[0])
                PONAV_volume_fraction = float(row.split("PONAV_Volume_fraction:")[1].split()[0])
                VPOV = POAV_volume_fraction + PONAV_volume_fraction
                GPOV = VPOV / density

    # Construct a dataframe for geometric parameters
    basename = f"{name}_primitive"
    geo_dict = {
        "name": basename,
        "cif_file": f"{name}_primitive.cif",
        "Di": largest_included_sphere,
        "Df": largest_free_sphere,
        "Dif": largest_included_sphere_along_free_sphere_path,
        "cell_v": unit_cell_volume,
        "VSA": VSA,
        "GSA": GSA,
        "VPOV": VPOV,
        "GPOV": GPOV,
        "POAV_vol_frac": POAV_volume_fraction,
        "PONAV_vol_frac": PONAV_volume_fraction,
        "GPOAV": GPOAV,
        "GPONAV": GPONAV,
        "POAV": POAV,
        "PONAV": PONAV
    }
    geo_df = pd.DataFrame([geo_dict])
    geo_df.to_csv(os.path.join(zeo_folder, "geometric_parameters.csv"), index=False)

    # Check the RACs log
    rac_log_path = os.path.join(RACs_folder, "RAC_getter_log.txt")
    if not os.path.exists(rac_log_path):
        print("RAC_getter_log.txt not found. RAC generation might have failed.")
        return 'FAILED'
    else:
        with open(rac_log_path, 'r') as f:
            if f.readline().strip() == "FAILED":
                print("RAC generation failed.")
                return 'FAILED'

    # Now merge geometric info with the 3 CSV files from RAC_getter
    try:
        lc_df = pd.read_csv(os.path.join(RACs_folder, "lc_descriptors.csv"))
        sbu_df = pd.read_csv(os.path.join(RACs_folder, "sbu_descriptors.csv"))
        linker_df = pd.read_csv(os.path.join(RACs_folder, "linker_descriptors.csv"))
    except Exception:
        return 'FAILED'

    # Take the mean across rows and convert to single-row dataframes
    lc_df = lc_df.mean().to_frame().T
    sbu_df = sbu_df.mean().to_frame().T
    linker_df = linker_df.mean().to_frame().T

    # Merge all into one big dataframe
    merged_df = pd.concat([geo_df, lc_df, sbu_df, linker_df], axis=1)

    # Write out
    merged_folder = os.path.join(temp_file_folder, "merged_descriptors")
    os.makedirs(merged_folder, exist_ok=True)
    merged_df.to_csv(os.path.join(merged_folder, f"{name}_descriptors_2.csv"), index=False)

    return 'SUCCESS'


# --------------------------------------------------------------------------------------
# 3) OPTIONAL: COMMAND-LINE INTERFACE
# --------------------------------------------------------------------------------------

def main():
    """
    Allows the script to be run from the command line, providing arguments
    for name, structure, prediction_type, and session_id.
    """
    parser = argparse.ArgumentParser(
        description="Generate descriptors (RACs and Zeo++) for a given MOF.")
    
    parser.add_argument("--name", required=True, help="Name of the MOF.")
    parser.add_argument("--structure", required=True,
                        help="Path to the CIF file OR raw CIF text. For simplicity, assume path.")
    parser.add_argument("--prediction_type", default="water",
                        help="Type of prediction (water or acid). Defaults to 'water'.")
    parser.add_argument("--session_id", default="1234",
                        help="Session ID to create unique temp folder. Defaults to '1234'.")
    
    args = parser.parse_args()

    # Read the CIF file contents if the user provided a path.
    # (If you prefer to accept raw text instead, remove the file-read logic.)
    if os.path.isfile(args.structure):
        with open(args.structure, 'r') as f:
            cif_contents = f.read()
    else:
        # If `args.structure` is NOT a file path, treat it as raw CIF text
        cif_contents = args.structure

    # Call the function
    result = descriptor_generator_2(
        name=args.name,
        structure=cif_contents,
        prediction_type=args.prediction_type,
        session_id=args.session_id
    )

    print("Result:", result)


# Standard Python "entry point"
if __name__ == "__main__":
    main()
