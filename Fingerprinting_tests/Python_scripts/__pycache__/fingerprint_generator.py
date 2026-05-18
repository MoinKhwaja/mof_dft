import os
import shutil
import subprocess
import pandas as pd
import numpy as np
from molSimplify.Informatics.MOF.MOF_descriptors import get_primitive, get_MOF_descriptors

MOFSIMPLIFY_PATH = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Fingerprinting_tests/"  # Update this path

def generate_descriptors(name, structure, prediction_type='water', is_entry=False):
    """
    Generate RACs and geometric descriptors for a given MOF.

    :param name: str, the name of the MOF.
    :param structure: str, the text content of the CIF file.
    :param prediction_type: str, either 'water' or 'acid'.
    :param is_entry: bool, indicates whether to skip descriptor generation.
    :return: str, 'SUCCESS' if successful, 'FAILED' otherwise.
    """
    session_id = "default_session"  # Replace with dynamic session ID if needed
    temp_file_folder = os.path.join(MOFSIMPLIFY_PATH, f"temp_file_creation_{session_id}/")
    cif_folder = os.path.join(temp_file_folder, "cifs/")
    RACs_folder = os.path.join(temp_file_folder, f"feature_generation/{prediction_type}_RACs/")
    zeo_folder = os.path.join(temp_file_folder, f"feature_generation/{prediction_type}_zeo++/")
    descriptors_folder = os.path.join(temp_file_folder, "merged_descriptors/")

    # Create temporary directories
    os.makedirs(cif_folder, exist_ok=True)
    os.makedirs(RACs_folder, exist_ok=True)
    os.makedirs(zeo_folder, exist_ok=True)
    os.makedirs(descriptors_folder, exist_ok=True)

    # Write CIF file
    cif_file_path = os.path.join(cif_folder, f"{name}.cif")
    with open(cif_file_path, 'w') as cif_file:
        cif_file.write(structure)

    if is_entry:
        return "SUCCESS"

    # Generate primitive CIF
    try:
        primitive_cif_path = os.path.join(cif_folder, f"{name}_primitive.cif")
        get_primitive(cif_file_path, primitive_cif_path)
    except ValueError:
        shutil.copy(cif_file_path, primitive_cif_path)

    # Run Zeo++ commands
    try:
        cmd1 = f"{MOFSIMPLIFY_PATH}zeo++-0.3/network -ha -res {zeo_folder}{name}_pd.txt {primitive_cif_path}"
        cmd2 = f"{MOFSIMPLIFY_PATH}zeo++-0.3/network -sa 1.4 1.4 10000 {zeo_folder}{name}_sa.txt {primitive_cif_path}"
        cmd3 = f"{MOFSIMPLIFY_PATH}zeo++-0.3/network -volpo 1.4 1.4 10000 {zeo_folder}{name}_pov.txt {primitive_cif_path}"

        processes = [subprocess.Popen(cmd, shell=True) for cmd in [cmd1, cmd2, cmd3]]
        for process in processes:
            process.communicate()
    except Exception as e:
        print(f"Failed to execute Zeo++ commands: {e}")
        return "FAILED"

    # Parse geometric descriptors
    geo_df = parse_geometric_descriptors(name, zeo_folder)
    if geo_df is None:
        return "FAILED"

    # Generate RAC descriptors
    rac_df = generate_racs(cif_folder, name, RACs_folder)
    if rac_df is None:
        return "FAILED"

    # Merge and save descriptors
    merged_df = pd.concat([geo_df, rac_df], axis=1)
    merged_df['name'] = name
    merged_df['cif_file'] = cif_file_path
    output_file = os.path.join(descriptors_folder, f"{name}_descriptors_{prediction_type}.csv")
    merged_df.to_csv(output_file, index=False)
    print(f"Descriptors saved to {output_file}")
    return "SUCCESS"


def parse_geometric_descriptors(name, zeo_folder):
    """
    Parse geometric descriptors from Zeo++ output files.

    :param name: str, name of the MOF.
    :param zeo_folder: str, path to Zeo++ output folder.
    :return: pd.DataFrame or None if parsing fails.
    """
    try:
        largest_included_sphere = largest_free_sphere = largest_included_sphere_along_free_sphere_path = np.nan
        unit_cell_volume = VSA = GSA = POAV = PONAV = GPOAV = GPONAV = np.nan
        POAV_volume_fraction = PONAV_volume_fraction = VPOV = GPOV = np.nan

        with open(os.path.join(zeo_folder, f"{name}_pd.txt")) as f:
            data = f.readlines()[0].split()
            largest_included_sphere = float(data[1])
            largest_free_sphere = float(data[2])
            largest_included_sphere_along_free_sphere_path = float(data[3])

        with open(os.path.join(zeo_folder, f"{name}_sa.txt")) as f:
            data = f.readlines()[0]
            unit_cell_volume = float(data.split("Unitcell_volume:")[1].split()[0])
            VSA = float(data.split("ASA_m^2/cm^3:")[1].split()[0])
            GSA = float(data.split("ASA_m^2/g:")[1].split()[0])

        with open(os.path.join(zeo_folder, f"{name}_pov.txt")) as f:
            data = f.readlines()[0]
            POAV = float(data.split("POAV_A^3:")[1].split()[0])
            PONAV = float(data.split("PONAV_A^3:")[1].split()[0])
            GPOAV = float(data.split("POAV_cm^3/g:")[1].split()[0])
            GPONAV = float(data.split("PONAV_cm^3/g:")[1].split()[0])
            POAV_volume_fraction = float(data.split("POAV_Volume_fraction:")[1].split()[0])
            PONAV_volume_fraction = float(data.split("PONAV_Volume_fraction:")[1].split()[0])
            VPOV = POAV_volume_fraction + PONAV_volume_fraction
            GPOV = VPOV / float(data.split("Density:")[1].split()[0])

        geo_dict = {
            'Di': largest_included_sphere,
            'Df': largest_free_sphere,
            'Dif': largest_included_sphere_along_free_sphere_path,
            'cell_v': unit_cell_volume,
            'VSA': VSA,
            'GSA': GSA,
            'POAV': POAV,
            'PONAV': PONAV,
            'GPOAV': GPOAV,
            'GPONAV': GPONAV,
            'POAV_vol_frac': POAV_volume_fraction,
            'PONAV_vol_frac': PONAV_volume_fraction,
            'VPOV': VPOV,
            'GPOV': GPOV,
        }
        return pd.DataFrame([geo_dict])
    except Exception as e:
        print(f"Error parsing geometric descriptors: {e}")
        return None


def generate_racs(cif_folder, name, RACs_folder):
    """
    Generate RAC descriptors by calling molSimplify's `get_MOF_descriptors`.

    :param cif_folder: str, path to the CIF folder.
    :param name: str, the name of the MOF.
    :param RACs_folder: str, the folder to save RAC descriptors.
    :return: pd.DataFrame or None if generation fails.
    """
    try:
        # Log file for RAC generation
        with open(os.path.join(RACs_folder, 'RAC_getter_log.txt'), 'w') as log:
            try:
                full_names, full_descriptors = get_MOF_descriptors(
                    os.path.join(cif_folder, f"{name}_primitive.cif"), 3,
                    path=RACs_folder, xyzpath=os.path.join(RACs_folder, f"{name}.xyz")
                )
            except (ValueError, NotImplementedError, AssertionError):
                log.write("FAILED")
                return None

            if len(full_names) <= 1 and len(full_descriptors) <= 1:
                log.write("FAILED")
                return None

        # Parse RAC descriptor files
        lc_df = pd.read_csv(os.path.join(RACs_folder, "lc_descriptors.csv")).mean().to_frame().transpose()
        sbu_df = pd.read_csv(os.path.join(RACs_folder, "sbu_descriptors.csv")).mean().to_frame().transpose()
        linker_df = pd.read_csv(os.path.join(RACs_folder, "linker_descriptors.csv")).mean().to_frame().transpose()
        return pd.concat([lc_df, sbu_df, linker_df], axis=1)
    except Exception as e:
        print(f"Failed to generate RAC descriptors: {e}")
        return None


if __name__ == "__main__":
    name = "qmof-2b10e5e"
    cif_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Fingerprinting_tests/CIFs/qmof-2b10e5e.cif"  # Replace with the actual CIF file path
    
    # Read the CIF content from the file
    with open(cif_path, 'r') as f:
        structure = f.read()
    
    # Generate descriptors
    result = generate_descriptors(name, structure, prediction_type="water", is_entry=False)
    print(f"Result: {result}")

