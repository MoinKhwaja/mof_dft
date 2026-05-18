from solvent_ann import predict_solvent_stability

# Paths
descriptor_csv = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Solvent_Stability/qmof-0a0bcfa_descriptors.csv"
output_csv = "/Users/moinkhwaja/Documents/GitHub/HTS_MOF_Hydrogenation/Screening_Scripts/Solvent_Stability/output/output.csv"

# Run prediction
predict_solvent_stability(descriptor_csv, output_csv)
