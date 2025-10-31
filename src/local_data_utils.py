"""
Local Data Utilities for Offline Genetic Analysis

This module provides functions to load and query local genetic datasets
without requiring external API calls.
"""

import os
import sqlite3
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .utils import CONFIG

# Path to datasets directory
DATASETS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "datasets")


class LocalGeneticData:
    """Class to manage local genetic datasets."""

    def __init__(self):
        self._gene_df = None
        self._snp_df = None
        self._pop_freq_df = None
        self._clinvar_db_path = None
        self._loaded = False

    def load_datasets(self):
        """Load all local datasets into memory."""
        if self._loaded:
            return

        try:
            # Load gene annotations
            gene_path = os.path.join(DATASETS_DIR, "gene_annotations.tsv")
            if os.path.exists(gene_path):
                self._gene_df = pd.read_csv(
                    gene_path, sep="\t", dtype={"chromosome": str}
                )
                self._gene_df["gene_symbol"] = self._gene_df["gene_symbol"].str.upper()

            # Load SNP annotations
            snp_path = os.path.join(DATASETS_DIR, "snp_annotations.tsv")
            if os.path.exists(snp_path):
                self._snp_df = pd.read_csv(
                    snp_path, sep="\t", dtype={"chromosome": str}
                )

            # Load population frequencies
            pop_path = os.path.join(DATASETS_DIR, "population_frequencies.tsv")
            if os.path.exists(pop_path):
                self._pop_freq_df = pd.read_csv(pop_path, sep="\t")

            self._loaded = True

        except Exception as e:
            print(f"Error loading local datasets: {e}")

    def get_gene_info(self, gene_symbol: str) -> Optional[Dict]:
        """Get information for a specific gene."""
        if not self._loaded:
            self.load_datasets()

        if self._gene_df is None:
            return None

        gene_symbol = gene_symbol.upper()
        gene_row = self._gene_df[self._gene_df["gene_symbol"] == gene_symbol]

        if gene_row.empty:
            return None

        row = gene_row.iloc[0]
        return {
            "gene_symbol": row["gene_symbol"],
            "chromosome": row["chromosome"],
            "start": int(row["start"]),
            "end": int(row["end"]),
            "strand": row["strand"],
            "description": row["description"],
        }

    def get_snp_info(self, rsid: str) -> Optional[Dict]:
        """Get information for a specific SNP."""
        if not self._loaded:
            self.load_datasets()

        if self._snp_df is None:
            return None

        snp_row = self._snp_df[self._snp_df["rsid"] == rsid]

        if snp_row.empty:
            return None

        row = snp_row.iloc[0]
        return {
            "rsid": row["rsid"],
            "chromosome": row["chromosome"],
            "position": int(row["position"]),
            "ref_allele": row["ref_allele"],
            "alt_allele": row["alt_allele"],
            "maf": float(row["maf"]),
            "clinical_significance": row["clinical_significance"],
            "gene": row["gene"],
        }

    def get_population_frequencies(self, rsid: str) -> Optional[pd.DataFrame]:
        """Get population frequencies for a specific SNP."""
        if not self._loaded:
            self.load_datasets()

        if self._pop_freq_df is None:
            return None

        freq_data = self._pop_freq_df[self._pop_freq_df["rsid"] == rsid]

        if freq_data.empty:
            return None

        return freq_data.copy()

    def search_genes_by_chromosome(self, chromosome: str) -> pd.DataFrame:
        """Search for genes on a specific chromosome."""
        if not self._loaded:
            self.load_datasets()

        if self._gene_df is None:
            return pd.DataFrame()

        return self._gene_df[self._gene_df["chromosome"] == chromosome].copy()

    def search_snps_by_gene(self, gene_symbol: str) -> pd.DataFrame:
        """Search for SNPs associated with a specific gene."""
        if not self._loaded:
            self.load_datasets()

        if self._snp_df is None:
            return pd.DataFrame()

        gene_symbol = gene_symbol.upper()
        return self._snp_df[self._snp_df["gene"] == gene_symbol].copy()

    def get_chromosome_stats(self) -> Dict[str, int]:
        """Get statistics about genes per chromosome."""
        if not self._loaded:
            self.load_datasets()

        if self._gene_df is None:
            return {}

        return self._gene_df["chromosome"].value_counts().to_dict()

    def get_clinical_snps(
        self, significance_filter: Optional[str] = None
    ) -> pd.DataFrame:
        """Get SNPs with clinical significance."""
        if not self._loaded:
            self.load_datasets()

        if self._snp_df is None:
            return pd.DataFrame()

        df = self._snp_df.copy()

        if significance_filter:
            df = df[
                df["clinical_significance"].str.lower() == significance_filter.lower()
            ]

        return df

    def _create_clinvar_sqlite_db(self, tsv_path: str) -> str:
        """Create SQLite database from ClinVar TSV with indexes."""
        db_path = tsv_path.replace(".tsv", ".db")
        if (
            os.path.exists(db_path)
            and not CONFIG["performance"]["enable_sqlite_indexes"]
        ):
            return db_path

        try:
            # Read TSV
            df = pd.read_csv(tsv_path, sep="\t", dtype={"rsid": str})

            # Create SQLite DB
            conn = sqlite3.connect(db_path)
            df.to_sql("clinvar_variants", conn, if_exists="replace", index=False)

            # Create indexes on key fields
            cursor = conn.cursor()
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_rsid ON clinvar_variants(rsid)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_gene ON clinvar_variants(Gene)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_clnsig ON clinvar_variants(CLNSIG)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_chromosome ON clinvar_variants(Chromosome)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_position ON clinvar_variants(Position)"
            )

            conn.commit()
            conn.close()

            print(f"Created SQLite database with indexes: {db_path}")
            return db_path

        except Exception as e:
            print(f"Error creating SQLite database: {e}")
            return tsv_path  # Fallback to TSV

    def query_clinvar_sqlite(
        self,
        rsid: Optional[str] = None,
        gene: Optional[str] = None,
        clnsig: Optional[str] = None,
    ) -> pd.DataFrame:
        """Query ClinVar data from SQLite database."""
        if not self._clinvar_db_path or not os.path.exists(self._clinvar_db_path):
            return pd.DataFrame()

        try:
            conn = sqlite3.connect(self._clinvar_db_path)
            query = "SELECT * FROM clinvar_variants WHERE 1=1"
            params = []

            if rsid:
                query += " AND rsid = ?"
                params.append(rsid)
            if gene:
                query += " AND Gene = ?"
                params.append(gene)
            if clnsig:
                query += " AND CLNSIG = ?"
                params.append(clnsig)

            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            return df

        except Exception as e:
            print(f"Error querying SQLite database: {e}")
            return pd.DataFrame()


# Global instance
local_data = LocalGeneticData()


def get_gene_info_local(gene_symbol: str) -> Optional[Dict]:
    """Convenience function to get gene information."""
    return local_data.get_gene_info(gene_symbol)


def get_snp_info_local(rsid: str) -> Optional[Dict]:
    """Convenience function to get SNP information."""
    return local_data.get_snp_info(rsid)


def get_population_frequencies_local(rsid: str) -> Optional[pd.DataFrame]:
    """Convenience function to get population frequencies."""
    return local_data.get_population_frequencies(rsid)


def get_clinvar_pathogenic_variants_local() -> Optional[pd.DataFrame]:
    """Get local ClinVar pathogenic variants database."""
    clinvar_tsv_path = os.path.join(
        os.path.dirname(__file__), "clinvar_pathogenic_variants.tsv"
    )
    if not os.path.exists(clinvar_tsv_path):
        # Try to find it in the root directory
        clinvar_tsv_path = os.path.join(
            os.path.dirname(__file__), "..", "clinvar_pathogenic_variants.tsv"
        )
        if not os.path.exists(clinvar_tsv_path):
            return None

    if CONFIG["performance"]["enable_sqlite_indexes"]:
        try:
            # Use SQLite with indexes
            local_data = LocalGeneticData()
            local_data._clinvar_db_path = local_data._create_clinvar_sqlite_db(
                clinvar_tsv_path
            )
            # Return all data for compatibility
            return local_data.query_clinvar_sqlite()
        except Exception as e:
            print(f"Error loading ClinVar SQLite data: {e}. Falling back to TSV.")

    # Fallback to TSV
    try:
        return pd.read_csv(clinvar_tsv_path, sep="\t", dtype={"rsid": str})
    except Exception as e:
        print(f"Error loading ClinVar TSV data: {e}")

    return None


def load_local_datasets():
    """Load all local datasets."""
    local_data.load_datasets()


# Initialize datasets on import
try:
    load_local_datasets()
except Exception as e:
    print(f"Warning: Could not load local datasets: {e}")
    print("Some offline features may not be available.")
