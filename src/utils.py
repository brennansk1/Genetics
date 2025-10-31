import os
import time
from functools import wraps
from io import BytesIO, StringIO

import pandas as pd
import polars as pl
import requests
import streamlit as st

# Configuration section for performance optimizations
CONFIG = {
    "performance": {
        "enable_parallel_processing": False,  # Toggle for Dask parallel processing
        "enable_redis_caching": False,  # Toggle for Redis API response caching
        "enable_sqlite_indexes": False,  # Toggle for SQLite indexes on ClinVar data
        "enable_gpu_prs": False,  # Toggle for GPU-accelerated PRS calculations
    },
    "caching": {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "cache_ttl": 3600,  # 1 hour default TTL
    },
    "parallel": {
        "num_workers": None,  # None means use Dask default
        "scheduler": "threads",  # 'threads', 'processes', or 'synchronous'
    },
    "gpu": {
        "device": "cuda",  # 'cuda' or 'cpu' fallback
        "memory_limit": None,  # GPU memory limit in MB
    },
    "ux_enhancements": {
        "enable_ai_coach": False,  # Toggle for AI-Powered Genetic Health Coach
        "enable_pwa": False,  # Toggle for Progressive Web App features
        "enable_3d_browser": False,  # Toggle for Interactive 3D Genome Browser
    },
    "api_keys": {
        "openai_api_key": os.getenv(
            "OPENAI_API_KEY", None
        ),  # OpenAI API key for AI Coach
    },
}


def api_call_with_retry(max_retries=3, delay=1):
    """
    Decorator for API calls with retry logic and error handling.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2**attempt))  # Exponential backoff
                        continue
                    else:
                        st.error(
                            f"API call failed after {max_retries} attempts: {str(e)}"
                        )
                        return None
                except Exception as e:
                    last_exception = e
                    st.error(f"Unexpected error in API call: {str(e)}")
                    return None
            return None

        return wrapper

    return decorator


def parse_dna_file(uploaded_file, file_format="AncestryDNA"):
    """
    Parses the uploaded DNA file supporting multiple formats.
    """
    string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))

    if file_format == "AncestryDNA":
        # Find the start of the data
        lines = string_data.readlines()
        start_index = 0
        for i, line in enumerate(lines):
            if line.startswith("rsid"):
                start_index = i
                break

        # Read the data into a Polars DataFrame
        csv_content = "".join(lines[start_index:])
        df = pl.read_csv(
            BytesIO(csv_content.encode("utf-8")),
            separator="\t",
            dtypes={"rsid": pl.Utf8},
        )

        # Combine allele1 and allele2 to create genotype
        if "allele1" in df.columns and "allele2" in df.columns:
            df = df.with_columns(
                (pl.col("allele1") + pl.col("allele2")).alias("genotype")
            )
            df = df.drop(["allele1", "allele2"])

    elif file_format == "23andMe":
        # 23andMe format: rsid, chromosome, position, genotype
        df = pl.read_csv(
            BytesIO(string_data.getvalue().encode("utf-8")),
            separator="\t",
            comment_prefix="#",
            has_header=False,
            new_columns=["rsid", "chromosome", "position", "genotype"],
            dtypes={"rsid": pl.Utf8},
        )

        # Filter out invalid genotypes and non-SNP entries
        valid_genotypes = [
            "AA",
            "CC",
            "GG",
            "TT",
            "AC",
            "AG",
            "AT",
            "CG",
            "CT",
            "GT",
            "--",
            "II",
            "DD",
            "DI",
            "ID",
        ]
        df = df.filter(pl.col("genotype").is_in(valid_genotypes))

    elif file_format == "MyHeritage":
        # MyHeritage format: similar to 23andMe but may have different column names
        df = pl.read_csv(
            BytesIO(string_data.getvalue().encode("utf-8")),
            separator="\t",
            comment_prefix="#",
            dtypes={"RSID": pl.Utf8},
        )
        if "RSID" in df.columns:
            df = df.rename({"RSID": "rsid"})
        df = df.with_columns(pl.col("RESULT").alias("genotype"))
        df = df.select(["rsid", "genotype"])

    elif file_format == "LivingDNA":
        # LivingDNA format: rsid, genotype
        df = pl.read_csv(
            BytesIO(string_data.getvalue().encode("utf-8")),
            separator="\t",
            dtypes={"rsid": pl.Utf8},
        )

    else:
        raise ValueError(f"Unsupported file format: {file_format}")

    # Standardize columns
    required_cols = ["rsid", "genotype"]
    if "chromosome" in df.columns:
        required_cols.append("chromosome")
    if "position" in df.columns:
        required_cols.append("position")

    df = df.select(required_cols)
    df = df.drop_nulls(subset=["rsid", "genotype"])

    return df


def analyze_wellness_snps(dna_data):
    """
    Analyzes the user's DNA data for a predefined list of wellness-related SNPs.
    """
    # SNP data sourced from GWAS Catalog, ClinVar, and literature reviews
    snps_to_analyze = {
        # Nutritional Genetics
        "rs4988235": {
            "name": "Lactose Tolerance",
            "gene": "MCM6",
            "interp": {
                "CC": "Lactase non-persistent",
                "CT": "Lactase non-persistent",
                "TT": "Lactase persistent",
            },
        },
        "rs762551": {
            "name": "Caffeine Metabolism",
            "gene": "CYP1A2",
            "interp": {
                "CC": "Slow metabolizer",
                "CT": "Intermediate",
                "TT": "Fast metabolizer",
            },
        },
        "rs601338": {
            "name": "Vitamin B12",
            "gene": "FUT2",
            "interp": {"AA": "Normal", "AG": "Reduced", "GG": "Low"},
        },
        "rs1801133": {
            "name": "Vitamin B12",
            "gene": "MTHFR",
            "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Reduced"},
        },
        "rs7041": {
            "name": "Vitamin D",
            "gene": "GC",
            "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Low"},
        },
        "rs4588": {
            "name": "Vitamin D",
            "gene": "GC",
            "interp": {"AA": "Normal", "AG": "Intermediate", "GG": "Low"},
        },
        "rs2282679": {
            "name": "Vitamin D",
            "gene": "GC",
            "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Low"},
        },
        "rs10741657": {
            "name": "Vitamin D",
            "gene": "CYP2R1",
            "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Low"},
        },
        # Fitness Genetics
        "rs1815739": {
            "name": "Athletic Performance (Power/Sprint vs. Endurance)",
            "gene": "ACTN3",
            "interp": {"CC": "Endurance", "CT": "Mixed", "TT": "Power/Sprint"},
        },
        # Holistic Pathway Analysis
        "rs4680": {
            "name": "Methylation (COMT)",
            "gene": "COMT",
            "interp": {
                "GG": "Low activity",
                "AG": "Intermediate",
                "AA": "High activity",
            },
        },
        # Longevity and Cellular Aging Markers
        "rs7726159": {
            "name": "Telomere Length (TERC)",
            "gene": "TERC",
            "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Short"},
        },
        "rs2736100": {
            "name": "Telomere Length (TERT)",
            "gene": "TERT",
            "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Short"},
        },
        "rs11191865": {
            "name": "Telomere Length (OBFC1)",
            "gene": "OBFC1",
            "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "Short"},
        },
        "rs2802292": {
            "name": "Longevity (FOXO3)",
            "gene": "FOXO3",
            "interp": {"AA": "Normal", "AG": "Intermediate", "GG": "Longevity"},
        },
        "rs429358": {
            "name": "Longevity (APOE e2)",
            "gene": "APOE",
            "interp": {"CC": "Normal", "CT": "Carrier", "TT": "e2/e2"},
        },
        "rs7412": {
            "name": "Longevity (APOE e2)",
            "gene": "APOE",
            "interp": {"CC": "Normal", "CT": "Carrier", "TT": "e2/e2"},
        },
        # Chronobiology and Sleep Traits
        "rs57875989": {
            "name": "Chronotype (PER3 VNTR)",
            "gene": "PER3",
            "interp": {"--": "Not determined"},
        },
        "rs1801260": {
            "name": "Chronotype (CLOCK)",
            "gene": "CLOCK",
            "interp": {"CC": "Morning", "CT": "Intermediate", "TT": "Evening"},
        },
        "rs11063118": {
            "name": "Chronotype (RGS16)",
            "gene": "RGS16",
            "interp": {"CC": "Morning", "CT": "Intermediate", "TT": "Evening"},
        },
        "rs11252394": {
            "name": "Insomnia Risk (MEIS1)",
            "gene": "MEIS1",
            "interp": {"CC": "Normal", "CT": "Intermediate", "TT": "High risk"},
        },
        # Quirky Trait Report
        "rs713598": {
            "name": "Bitter Taste Perception",
            "gene": "TAS2R38",
            "interp": {"CC": "Taster", "CT": "Taster", "TT": "Non-taster"},
        },
        "rs1726866": {
            "name": "Bitter Taste Perception",
            "gene": "TAS2R38",
            "interp": {"GG": "Taster", "GA": "Taster", "AA": "Non-taster"},
        },
        "rs10246939": {
            "name": "Bitter Taste Perception",
            "gene": "TAS2R38",
            "interp": {"CC": "Taster", "CT": "Taster", "TT": "Non-taster"},
        },
        "rs10427255": {
            "name": "Photic Sneeze Reflex",
            "gene": "ZEB2",
            "interp": {"CC": "No reflex", "CT": "Carrier", "TT": "Reflex"},
        },
        "rs4481887": {
            "name": "Asparagus Metabolite Detection",
            "gene": "OR2M7",
            "interp": {"AA": "Detector", "AG": "Detector", "GG": "Non-detector"},
        },
    }

    results = {}

    for rsid, info in snps_to_analyze.items():
        # Check if rsid is in the index (processed data) or as a column (raw data)
        if rsid in dna_data.index:
            genotype = dna_data.loc[rsid, "genotype"]
            results[rsid] = {
                "name": info["name"],
                "gene": info["gene"],
                "genotype": genotype,
                "interp": info.get("interp", {}),
            }
        elif "rsid" in dna_data.columns and rsid in dna_data["rsid"].values:
            user_genotype = dna_data[dna_data["rsid"] == rsid]
            genotype = user_genotype.iloc[0]["genotype"]
            results[rsid] = {
                "name": info["name"],
                "gene": info["gene"],
                "genotype": genotype,
                "interp": info.get("interp", {}),
            }
        else:
            results[rsid] = {
                "name": info["name"],
                "gene": info["gene"],
                "genotype": "Not Found",
                "interp": info.get("interp", {}),
            }

    return results
