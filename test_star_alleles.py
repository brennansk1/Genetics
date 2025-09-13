from src.run_analysis import process_dna_file
from src.pgx_star_alleles import StarAlleleCaller

# Load DNA data
dna_file = "AncestryDNA.txt"
build = "GRCh37"
df = process_dna_file(dna_file, build)

# Test star allele calling for CYP2C19
caller = StarAlleleCaller()
result = caller.call_star_alleles('CYP2C19', df)
print("CYP2C19 Star Allele Result:")
print(result)

# Test another gene
result2 = caller.call_star_alleles('CYP2D6', df)
print("\nCYP2D6 Star Allele Result:")
print(result2)