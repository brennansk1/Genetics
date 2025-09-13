#!/usr/bin/env python3
"""
Test backward compatibility with existing PRS implementation
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_legacy_prs_models():
    """Test that legacy PRS models still work"""
    print("Testing legacy PRS models...")

    # Import the legacy models for backward compatibility testing
    from snp_data import legacy_prs_models as legacy_models, guidance_data

    # Check if we have the expected traits
    expected_traits = ["Coronary Artery Disease", "Type 2 Diabetes", "Atrial Fibrillation"]

    for trait in expected_traits:
        if trait in legacy_models:
            model = legacy_models[trait]
            if 'rsid' in model and 'effect_allele' in model and 'effect_weight' in model:
                print(f"[OK] {trait}: {len(model['rsid'])} SNPs")
            else:
                print(f"[ERROR] {trait}: Missing required fields")
        else:
            print(f"[ERROR] {trait}: Not found in legacy models")

def test_guidance_data():
    """Test that guidance data still works"""
    print("\nTesting guidance data...")

    from snp_data import guidance_data

    expected_conditions = ["Coronary Artery Disease", "Type 2 Diabetes"]

    for condition in expected_conditions:
        if condition in guidance_data:
            data = guidance_data[condition]
            required_keys = ["lifestyle", "monitoring", "medical", "screening"]
            if all(key in data for key in required_keys):
                print(f"[OK] {condition}: Complete guidance data")
            else:
                print(f"[ERROR] {condition}: Missing guidance fields")
        else:
            print(f"[ERROR] {condition}: Not found in guidance data")

def test_old_render_prs_compatibility():
    """Test that old render_prs functionality would still work"""
    print("\nTesting render_prs compatibility...")

    # Simulate old usage pattern - use legacy models
    from snp_data import legacy_prs_models, guidance_data

    # Create sample DNA data
    dna_data = pd.DataFrame({
        'rsid': ['rs10757274', 'rs10757278', 'rs1333049'],
        'genotype': ['GG', 'GG', 'CC']
    })

    # Test old calculation method
    trait = "Coronary Artery Disease"
    if trait in legacy_prs_models:
        model_data = legacy_prs_models[trait]

        # Old calculation logic - create DataFrame properly
        prs_model_df = pd.DataFrame({
            'effect_allele': model_data['effect_allele'],
            'effect_weight': model_data['effect_weight']
        }, index=model_data['rsid'])

        merged_df = dna_data.join(prs_model_df, how='inner')

        if not merged_df.empty:
            merged_df['allele_count'] = merged_df.apply(lambda row: row['genotype'].upper().count(row['effect_allele']), axis=1)
            merged_df['score_contribution'] = merged_df['allele_count'] * merged_df['effect_weight']
            user_prs = merged_df['score_contribution'].sum()

            print(f"[OK] PRS calculation successful: {user_prs:.4f}")
        else:
            print(f"[ERROR] No overlapping SNPs found for {trait}")
    else:
        print(f"[ERROR] {trait} not found in legacy models")

def main():
    """Run backward compatibility tests"""
    print("=== Backward Compatibility Test ===\n")

    test_legacy_prs_models()
    test_guidance_data()
    test_old_render_prs_compatibility()

    print("\n=== Backward Compatibility Test Complete ===")

if __name__ == "__main__":
    main()