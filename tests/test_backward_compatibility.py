#!/usr/bin/env python3
"""
Test backward compatibility with existing PRS implementation
"""

import os
import sys

import pandas as pd

# Add parent directory to path for src imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_legacy_prs_models():
    """Test that legacy PRS models still work"""
    print("Testing legacy PRS models...")

    # Import the legacy models for backward compatibility testing
    from src.snp_data import get_legacy_prs_models
    legacy_models = get_legacy_prs_models()

    # Check if we have the expected traits
    expected_traits = [
        "Coronary Artery Disease",
        "Type 2 Diabetes",
        "Atrial Fibrillation",
    ]

    for trait in expected_traits:
        if trait in legacy_models:
            model = legacy_models[trait]
            if (
                "rsid" in model
                and "effect_allele" in model
                and "effect_weight" in model
            ):
                print(f"[OK] {trait}: {len(model['rsid'])} SNPs")
            else:
                print(f"[ERROR] {trait}: Missing required fields")
        else:
            print(f"[ERROR] {trait}: Not found in legacy models")





def test_old_render_prs_compatibility():
    """Test that old render_prs functionality would still work"""
    print("\nTesting render_prs compatibility...")

    # Simulate old usage pattern - use legacy models
    from src.snp_data import get_legacy_prs_models
    legacy_prs_models = get_legacy_prs_models()

    # Create sample DNA data
    dna_data = pd.DataFrame(
        {
            "rsid": ["rs10757274", "rs10757278", "rs1333049"],
            "genotype": ["GG", "GG", "CC"],
        }
    )

    # Test old calculation method
    trait = "Coronary Artery Disease"
    if trait in legacy_prs_models:
        model_data = legacy_prs_models[trait]

        # Old calculation logic - create DataFrame properly
        prs_model_df = pd.DataFrame(
            {
                "effect_allele": model_data["effect_allele"],
                "effect_weight": model_data["effect_weight"],
            },
            index=model_data["rsid"],
        )

        merged_df = dna_data.join(prs_model_df, how="inner")

        if not merged_df.empty:
            merged_df["allele_count"] = merged_df.apply(
                lambda row: row["genotype"].upper().count(row["effect_allele"]), axis=1
            )
            merged_df["score_contribution"] = (
                merged_df["allele_count"] * merged_df["effect_weight"]
            )
            user_prs = merged_df["score_contribution"].sum()

            print(f"[OK] PRS calculation successful: {user_prs:.4f}")
        else:
            print(f"[ERROR] No overlapping SNPs found for {trait}")
    else:
        print(f"[ERROR] {trait} not found in legacy models")


def main():
    """Run backward compatibility tests"""
    print("=== Backward Compatibility Test ===\n")

    test_legacy_prs_models()
    test_old_render_prs_compatibility()

    print("\n=== Backward Compatibility Test Complete ===")


if __name__ == "__main__":
    main()
