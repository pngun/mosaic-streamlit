# Names of common columns in Insights generated DataFrames
SAMPLE = "Sample"
SUBCLONE = "Subclone"
VARIANT = "Variant"
CELL = "Barcode"
WHITELIST = "Whitelist"
GENOME = "genome"

PROTEIN_ASSAY_PROTEIN = "Protein"

# Names of Annotations returned by the Variant API
CLINVAR = "clinvar"
GNOMAD = "allele_freq"
COSMIC = "cosmic"
DANN = "impact"
GENE = "gene"
IMPACT = "protein_coding_impact"
PROTEIN = "protein"
FUNCTION = "function"

# Names of columns present in the SNP frame of the MissionBio h5 files
CHROM = "CHROM"

POS = "POS"
REF = "REF"
ALT = "ALT"

# Names of the columns in whitelist
START = "start"
END = "end"
ALLELE_INFO = "allele_info"

# Columns that should always be present in the SNP dataframe
DEFAULT_ANNOTATION_COLUMNS = [
    FUNCTION,
    PROTEIN,
    IMPACT,
    CLINVAR,
    DANN,
]
