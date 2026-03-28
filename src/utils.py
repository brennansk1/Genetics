import os
import time
from functools import wraps
from io import BytesIO, StringIO
from typing import Dict, Any

import logging

import pandas as pd
import polars as pl
import requests
try:
    from .vcf_parser import parse_vcf_file
except Exception:
    parse_vcf_file = None

logger = logging.getLogger(__name__)

class AppConfig:
    """
    Configuration management class that loads settings from environment variables
    with sensible defaults.
    """
    def __init__(self):
        self.performance = {
            "enable_parallel_processing": self._get_bool("ENABLE_PARALLEL_PROCESSING", False),
            "enable_redis_caching": self._get_bool("ENABLE_REDIS_CACHING", False),
            "enable_sqlite_indexes": self._get_bool("ENABLE_SQLITE_INDEXES", False),
            "enable_gpu_prs": self._get_bool("ENABLE_GPU_PRS", False),
        }
        self.caching = {
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", 6379)),
            "redis_db": int(os.getenv("REDIS_DB", 0)),
            "cache_ttl": int(os.getenv("CACHE_TTL", 3600)),
        }
        self.parallel = {
            "num_workers": int(os.getenv("NUM_WORKERS")) if os.getenv("NUM_WORKERS") else None,
            "scheduler": os.getenv("SCHEDULER", "threads"),
        }
        self.gpu = {
            "device": os.getenv("GPU_DEVICE", "cuda"),
            "memory_limit": int(os.getenv("GPU_MEMORY_LIMIT")) if os.getenv("GPU_MEMORY_LIMIT") else None,
        }
        self.ux_enhancements = {
            "enable_ai_coach": self._get_bool("ENABLE_AI_COACH", False),
            "enable_pwa": self._get_bool("ENABLE_PWA", False),
            "enable_3d_browser": self._get_bool("ENABLE_3D_BROWSER", False),
        }
        self.api_keys = {
            "openai_api_key": os.getenv("OPENAI_API_KEY", None),
        }

    def _get_bool(self, key: str, default: bool) -> bool:
        val = os.getenv(key, str(default)).lower()
        return val in ("true", "1", "yes", "on")

    def to_dict(self) -> Dict[str, Any]:
        """Returns the configuration as a dictionary for backward compatibility."""
        return {
            "performance": self.performance,
            "caching": self.caching,
            "parallel": self.parallel,
            "gpu": self.gpu,
            "ux_enhancements": self.ux_enhancements,
            "api_keys": self.api_keys,
        }

# Singleton instance
_app_config = AppConfig()
# Backward compatibility
CONFIG = _app_config.to_dict()

def get_config() -> AppConfig:
    """Returns the application configuration singleton."""
    return _app_config


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
                        logger.error(
                            f"API call failed after {max_retries} attempts: {str(e)}"
                        )
                        return None
                except Exception as e:
                    last_exception = e
                    logger.error(f"Unexpected error in API call: {str(e)}")
                    return None
            return None

        return wrapper

    return decorator


def parse_dna_file(uploaded_file, file_format="AncestryDNA"):
    """
    Parses the uploaded DNA file supporting multiple formats.
    Accepts a file-like object with a getvalue() method or raw bytes/string.
    """
    if hasattr(uploaded_file, 'getvalue'):
        string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))
    elif isinstance(uploaded_file, bytes):
        string_data = StringIO(uploaded_file.decode("utf-8"))
    elif isinstance(uploaded_file, str):
        string_data = StringIO(uploaded_file)
    else:
        string_data = StringIO(uploaded_file.read().decode("utf-8"))

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
        if "RESULT" in df.columns:
            df = df.with_columns(pl.col("RESULT").alias("genotype"))

    elif file_format == "LivingDNA":
        # LivingDNA format: rsid, genotype
        df = pl.read_csv(
            BytesIO(string_data.getvalue().encode("utf-8")),
            separator="\t",
            dtypes={"rsid": pl.Utf8},
        )

    elif file_format == "VCF":
        # Use the dedicated VCF parser
        df = parse_vcf_file(uploaded_file)
        # Convert to Polars for consistency with other branches if needed, 
        # but parse_vcf_file returns Pandas DataFrame as per docstring.
        # The function returns df.to_pandas() at the end anyway, so we can just return it directly here?
        # No, the function expects to return df.to_pandas() at line 201.
        # So we should convert to Polars or just return early.
        return df

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

    # Convert to Pandas DataFrame for compatibility
    return df.to_pandas()


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
