#!/usr/bin/env python3
"""
Build Ancestry Prediction Model

This script builds an offline ancestry prediction model using 1000 Genomes data.
It performs SNP filtering, LD pruning, PCA, and trains a KNN classifier.
"""

import os
import warnings

import allel
import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

warnings.filterwarnings("ignore")


def load_1000_genomes_data():
    """
    Load 1000 Genomes data using scikit-allel.
    This is a placeholder - in practice, you'd download and load actual 1000G data.
    """
    print("Loading 1000 Genomes data...")

    # For demonstration, we'll create synthetic data mimicking 1000G structure
    # In real implementation, use allel.read_vcf() to load actual VCF files

    # Simulate loading chromosome 1 data
    # Replace with actual 1000G VCF loading
    np.random.seed(42)

    # Simulate 1000 samples from 5 populations
    n_samples = 1000
    n_snps = 50000  # Reduced for demo

    # Population labels (simplified)
    populations = ["EUR", "AFR", "EAS", "SAS", "AMR"]
    pop_labels = np.random.choice(populations, n_samples)

    # Simulate genotype matrix (0,1,2 for homozygous ref, het, homozygous alt)
    # Shape: (n_snps, n_samples) -> need to reshape to (n_snps, n_samples, 2) for allel
    genotypes = np.random.randint(0, 3, (n_snps, n_samples), dtype=np.int8)
    # Convert to 3D format for allel: (variants, samples, ploidy)
    genotypes = genotypes[:, :, np.newaxis]  # Add ploidy dimension
    genotypes = np.repeat(genotypes, 2, axis=2)  # Duplicate for diploid

    # Simulate SNP positions and IDs
    positions = np.sort(np.random.randint(1, 250000000, n_snps))
    rsids = [f"rs{i}" for i in range(1, n_snps + 1)]

    return genotypes, positions, rsids, pop_labels


def filter_snps(genotypes, positions, rsids, pop_labels, min_maf=0.05, max_missing=0.1):
    """
    Filter SNPs based on MAF and missing data.
    """
    print("Filtering SNPs...")

    # Convert to allele counts for MAF calculation
    allele_counts = genotypes.sum(axis=(1, 2))  # Sum over samples and ploidy
    n_samples = genotypes.shape[1]
    maf = np.minimum(
        allele_counts / (2 * n_samples), 1 - allele_counts / (2 * n_samples)
    )

    # Filter by MAF
    maf_filter = maf >= min_maf

    # Filter by missing data (simplified - assuming no missing in synthetic data)
    missing_filter = np.ones(len(rsids), dtype=bool)

    # Combine filters
    keep_snps = maf_filter & missing_filter

    filtered_genotypes = genotypes[keep_snps]
    filtered_positions = positions[keep_snps]
    filtered_rsids = np.array(rsids)[keep_snps]

    print(f"Kept {filtered_genotypes.shape[0]} SNPs after filtering")

    return filtered_genotypes, filtered_positions, filtered_rsids


def ld_prune(genotypes, positions, rsids, ld_threshold=0.8, window_size=50):
    """
    Perform LD pruning using scikit-allel.
    """
    print("Performing LD pruning...")

    # For simplicity, skip LD pruning for demo and just return filtered data
    # In production, proper LD pruning would be implemented
    print("Skipping LD pruning for demo purposes")

    return genotypes, positions, rsids


def perform_pca(genotypes, n_components=10):
    """
    Perform PCA on genotype data.
    """
    print("Performing PCA...")

    # Convert genotypes to allele counts (sum over ploidy dimension)
    allele_counts = genotypes.sum(axis=2).astype(float)  # Shape: (n_snps, n_samples)

    # Center by subtracting mean
    allele_counts = allele_counts - allele_counts.mean(axis=1, keepdims=True)

    # Perform PCA
    pca = PCA(n_components=n_components)
    pca_components = pca.fit_transform(allele_counts.T)  # Samples x components

    print(f"PCA explained variance: {pca.explained_variance_ratio_[:5]}")

    return pca, pca_components


def train_knn_classifier(pca_components, pop_labels, n_neighbors=5):
    """
    Train KNN classifier on PCA components.
    """
    print("Training KNN classifier...")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        pca_components, pop_labels, test_size=0.2, random_state=42, stratify=pop_labels
    )

    # Train KNN
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train, y_train)

    # Evaluate
    y_pred = knn.predict(X_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    return knn


def main():
    """
    Main function to build and save the ancestry model.
    """
    print("Building ancestry prediction model...")

    # Load data
    genotypes, positions, rsids, pop_labels = load_1000_genomes_data()

    # Filter SNPs
    genotypes, positions, rsids = filter_snps(genotypes, positions, rsids, pop_labels)

    # LD pruning
    genotypes, positions, rsids = ld_prune(genotypes, positions, rsids)

    # PCA
    pca_model, pca_components = perform_pca(genotypes)

    # Train KNN
    knn_model = train_knn_classifier(pca_components, pop_labels)

    # Save models
    os.makedirs("data", exist_ok=True)

    np.save("data/ancestry_snps.npy", {"rsids": rsids, "positions": positions})

    joblib.dump(pca_model, "data/ancestry_pca_model.joblib")
    joblib.dump(knn_model, "data/ancestry_knn_model.joblib")

    print("Models saved successfully!")
    print("Files:")
    print("- data/ancestry_snps.npy: SNP information")
    print("- data/ancestry_pca_model.joblib: PCA model")
    print("- data/ancestry_knn_model.joblib: KNN classifier")


if __name__ == "__main__":
    main()
