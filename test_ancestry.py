import pandas as pd

from src.ancestry_inference import infer_ancestry_from_snps
from src.run_analysis import process_dna_file

# Load DNA data
dna_file = "AncestryDNA.txt"
build = "GRCh37"
df = process_dna_file(dna_file, build)

# Run ancestry inference
result = infer_ancestry_from_snps(df)
print("Ancestry Inference Result:")
print(result)
