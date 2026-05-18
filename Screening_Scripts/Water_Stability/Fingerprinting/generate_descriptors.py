import os
import pandas as pd
import numpy as np
import subprocess
from molSimplify.Informatics.MOF.MOF_descriptors import get_primitive, get_MOF_descriptors

def descriptor_generator(name, cif_path, output_folder="./output"):
    """
    Generate a CSV file containing MOF descriptors (geometric and RAC) for the given MOF.

    :param name: str, the name of the MOF being analyzed.
    :param cif_path: str, the path to the input CIF file.
    :param output_folder: str, directory to save output descriptors.
    :return: None, saves the descriptor CSV in the specified folder.
    """

    # Hardcoded path to Zeo++
    zeo_path = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Water_Stability/Fingerprinting/zeo++-0.3/network"

    # Validate paths
    if not os.path.exists(cif_path):
        raise FileNotFoundError(f"CIF file not found at: {cif_path}")
    if not os.path.exists(zeo_path):
        raise FileNotFoundError(f"Zeo++ not found at: {zeo_path}")

    temp_file_folder = "./temp_file_creation/"
    cif_folder = os.path.join(temp_file_folder, "cifs/")
    RACs_folder = os.path.join(temp_file_folder, "feature_generation/RACs/")
    zeo_folder = os.path.join(temp_file_folder, "feature_generation/zeo++/")

    os.makedirs(cif_folder, exist_ok=True)
    os.makedirs(RACs_folder, exist_ok=True)
    os.makedirs(zeo_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    primitive_cif_path = os.path.join(cif_folder, f"{name}_primitive.cif")

    print(f"Input CIF: {cif_path}")
    print(f"Primitive CIF will be saved at: {primitive_cif_path}")

    # Try generating primitive structure
    try:
        get_primitive(cif_path, primitive_cif_path)
        print("Primitive structure generated successfully.")
    except Exception as e:
        print(f"Failed to generate primitive structure: {e}")
        return "FAILED"

    cmd1 = f"{zeo_path} -ha -res {zeo_folder}/{name}_pd.txt {primitive_cif_path}"
    cmd2 = f"{zeo_path} -sa 1.86 1.86 10000 {zeo_folder}/{name}_sa.txt {primitive_cif_path}"
    cmd3 = f"{zeo_path} -volpo 1.86 1.86 10000 {zeo_folder}/{name}_pov.txt {primitive_cif_path}"

    print("Running Zeo++ commands...")
    subprocess.run(cmd1, shell=True)
    subprocess.run(cmd2, shell=True)
    subprocess.run(cmd3, shell=True)

    geo_dict = parse_zeo_output(zeo_folder, name)
    result = process_mof(primitive_cif_path, name, RACs_folder)

    if result == "FAILED":
        print("RAC descriptor generation failed.")
        return "FAILED"

    geo_df = pd.DataFrame([geo_dict])
    lc_df = pd.read_csv(os.path.join(RACs_folder, "lc_descriptors.csv")).mean().to_frame().transpose()
    sbu_df = pd.read_csv(os.path.join(RACs_folder, "sbu_descriptors.csv")).mean().to_frame().transpose()
    linker_df = pd.read_csv(os.path.join(RACs_folder, "linker_descriptors.csv")).mean().to_frame().transpose()

    merged_df = pd.concat([geo_df, lc_df, sbu_df, linker_df], axis=1)
    output_file = os.path.join(output_folder, f"{name}_descriptors.csv")
    merged_df.to_csv(output_file, index=False)
    print(f"Descriptors saved to {output_file}")


def parse_zeo_output(zeo_folder, name):
    """
    Parse Zeo++ outputs to extract geometric descriptors.

    :param zeo_folder: str, directory containing Zeo++ output files.
    :param name: str, name of the MOF.
    :return: dict, containing geometric descriptors.
    """
    geo_dict = {
        "name": name,
        "Di": np.nan,
        "Df": np.nan,
        "Dif": np.nan,
        "cell_v": np.nan,
        "VSA": np.nan,
        "GSA": np.nan,
        "VPOV": np.nan,
        "GPOV": np.nan,
        "POAV_vol_frac": np.nan,
        "PONAV_vol_frac": np.nan,
        "GPOAV": np.nan,
        "GPONAV": np.nan,
        "POAV": np.nan,
        "PONAV": np.nan,
    }

    try:
        with open(os.path.join(zeo_folder, f"{name}_pd.txt")) as f:
            pd_data = f.readlines()
            geo_dict["Di"] = float(pd_data[0].split()[1])
            geo_dict["Df"] = float(pd_data[0].split()[2])
            geo_dict["Dif"] = float(pd_data[0].split()[3])

        with open(os.path.join(zeo_folder, f"{name}_sa.txt")) as f:
            sa_data = f.readlines()
            geo_dict["cell_v"] = float(sa_data[0].split("Unitcell_volume:")[1].split()[0])
            geo_dict["VSA"] = float(sa_data[0].split("ASA_m^2/cm^3:")[1].split()[0])
            geo_dict["GSA"] = float(sa_data[0].split("ASA_m^2/g:")[1].split()[0])

        with open(os.path.join(zeo_folder, f"{name}_pov.txt")) as f:
            pov_data = f.readlines()
            geo_dict["POAV"] = float(pov_data[0].split("POAV_A^3:")[1].split()[0])
            geo_dict["PONAV"] = float(pov_data[0].split("PONAV_A^3:")[1].split()[0])
            geo_dict["GPOAV"] = float(pov_data[0].split("POAV_cm^3/g:")[1].split()[0])
            geo_dict["GPONAV"] = float(pov_data[0].split("PONAV_cm^3/g:")[1].split()[0])

    except Exception as e:
        print(f"Error parsing Zeo++ output: {e}")

    return geo_dict


def process_mof(cif_path, mof_name, output_folder):
    """
    Process a single MOF CIF file to compute RAC descriptors.

    :param cif_path: str, path to the CIF file.
    :param mof_name: str, name of the MOF.
    :param output_folder: str, output folder for descriptors.
    :return: "FAILED" or tuple of descriptor data.
    """
    log_file = os.path.join(output_folder, "RAC_getter_log.txt")

    try:
        full_names, full_descriptors = get_MOF_descriptors(
            cif_path, 3, path=output_folder, xyzpath=os.path.join(output_folder, f"{mof_name}.xyz")
        )

        if len(full_names) <= 1 and len(full_descriptors) <= 1:
            with open(log_file, "w") as f:
                f.write("FAILED")
            print("RAC featurization failed.")
            return "FAILED"

        print("RAC descriptors successfully computed.")
        return full_names, full_descriptors

    except (ValueError, NotImplementedError, AssertionError) as e:
        with open(log_file, "w") as f:
            f.write("FAILED")
        print(f"Error during RAC computation: {e}")
        return "FAILED"
