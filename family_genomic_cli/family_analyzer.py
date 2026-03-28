import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from copied_modules.family_analysis import FamilyAnalyzer
from copied_modules.logging_utils import get_logger

logger = get_logger(__name__)

class AdvancedFamilyAnalyzer:
    """
    Advanced family genomic analyzer extending basic family analysis
    for comparative genetics and inheritance patterns.
    """

    def __init__(self, family_data: Dict[str, pd.DataFrame]):
        """
        Initialize with harmonized family data.

        Args:
            family_data: Dict with keys 'child', 'mother', 'father' (optional)
                         Each value is a DataFrame with SNP index and 'genotype' column
        """
        self.family_data = family_data
        self.child_df = family_data.get('child')
        self.mother_df = family_data.get('mother')
        self.father_df = family_data.get('father')

        if self.child_df is None:
            raise ValueError("Child genotype data is required")

        # Get common SNPs across available family members
        self.common_snps = set(self.child_df.index)
        if self.mother_df is not None:
            self.common_snps &= set(self.mother_df.index)
        if self.father_df is not None:
            self.common_snps &= set(self.father_df.index)

        logger.info(f"Found {len(self.common_snps)} common SNPs across family members")

    def trace_variant_origins(self, risk_variants: List[str]) -> Dict[str, Dict]:
        """
        For each risk variant in the child, determine inheritance pattern.

        Args:
            risk_variants: List of rsIDs to analyze

        Returns:
            Dict with rsID keys and inheritance info
        """
        logger.info(f"Tracing origins for {len(risk_variants)} risk variants")
        results = {}

        for rsid in risk_variants:
            if rsid not in self.child_df.index:
                logger.debug(f"Skipping {rsid}: not in child data")
                continue

            child_genotype = self.child_df.loc[rsid, 'genotype']
            if not child_genotype or child_genotype == '--':
                logger.debug(f"Skipping {rsid}: invalid child genotype")
                continue

            inheritance = {
                'child_genotype': child_genotype,
                'origin': 'unknown',
                'possible_sources': []
            }

            # Check mother
            if self.mother_df is not None and rsid in self.mother_df.index:
                mother_genotype = self.mother_df.loc[rsid, 'genotype']
                if mother_genotype and mother_genotype != '--':
                    if self._can_inherit_from(child_genotype, mother_genotype):
                        inheritance['possible_sources'].append('mother')

            # Check father
            if self.father_df is not None and rsid in self.father_df.index:
                father_genotype = self.father_df.loc[rsid, 'genotype']
                if father_genotype and father_genotype != '--':
                    if self._can_inherit_from(child_genotype, father_genotype):
                        inheritance['possible_sources'].append('father')

            # Determine origin
            if len(inheritance['possible_sources']) == 0:
                inheritance['origin'] = 'de_novo'
            elif len(inheritance['possible_sources']) == 1:
                inheritance['origin'] = inheritance['possible_sources'][0]
            else:
                inheritance['origin'] = 'inherited_from_both'

            results[rsid] = inheritance

        logger.info(f"Variant origin tracing completed: analyzed {len(results)} variants")
        logger.info(f"Variant origins results: {results}")
        return results

    def _can_inherit_from(self, child_gt: str, parent_gt: str) -> bool:
        """Check if child genotype can be inherited from parent genotype."""
        child_alleles = set(child_gt)
        parent_alleles = set(parent_gt)
        # Child must have at least one allele from parent
        return bool(child_alleles & parent_alleles)

    def detect_compound_heterozygosity(self, gene_variants: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """
        Detect compound heterozygous variants in genes.

        Args:
            gene_variants: Dict with gene names as keys, list of rsIDs as values

        Returns:
            Dict with genes that have compound het patterns
        """
        logger.info(f"Detecting compound heterozygosity for {len(gene_variants)} genes")
        results = {}

        for gene, variants in gene_variants.items():
            logger.debug(f"Analyzing compound het for gene {gene} with {len(variants)} variants")
            child_variants = []
            for rsid in variants:
                if rsid in self.child_df.index:
                    genotype = self.child_df.loc[rsid, 'genotype']
                    if genotype and len(set(genotype)) > 1:  # Heterozygous
                        # Check inheritance from different parents
                        origin = self._get_variant_origin(rsid)
                        if origin:
                            child_variants.append({
                                'rsid': rsid,
                                'genotype': genotype,
                                'origin': origin
                            })

            # Check if variants come from different parents
            if len(child_variants) >= 2:
                maternal = [v for v in child_variants if v['origin'] == 'mother']
                paternal = [v for v in child_variants if v['origin'] == 'father']

                if maternal and paternal:
                    results[gene] = {
                        'maternal_variants': maternal,
                        'paternal_variants': paternal,
                        'compound_het': True
                    }

        logger.info(f"Compound heterozygosity detection completed: found {len(results)} genes with compound het")
        logger.info(f"Compound heterozygosity results: {results}")
        return results

    def _get_variant_origin(self, rsid: str) -> Optional[str]:
        """Helper to get origin of a single variant."""
        if rsid not in self.child_df.index:
            return None

        child_gt = self.child_df.loc[rsid, 'genotype']
        if not child_gt or child_gt == '--':
            return None

        sources = []

        if self.mother_df is not None and rsid in self.mother_df.index:
            mother_gt = self.mother_df.loc[rsid, 'genotype']
            if mother_gt and self._can_inherit_from(child_gt, mother_gt):
                sources.append('mother')

        if self.father_df is not None and rsid in self.father_df.index:
            father_gt = self.father_df.loc[rsid, 'genotype']
            if father_gt and self._can_inherit_from(child_gt, father_gt):
                sources.append('father')

        if len(sources) == 1:
            return sources[0]
        return None

    def aggregate_shared_risks(self, individual_risks: Dict[str, Dict]) -> Dict:
        """
        Identify family-wide shared risk factors.

        Args:
            individual_risks: Dict with member keys ('child', 'mother', 'father')
                             and their risk analysis results

        Returns:
            Dict with shared risk patterns
        """
        logger.info("Aggregating shared risks across family members")
        shared_risks = {
            'high_prs_shared': [],
            'clinical_risks_shared': [],
            'carrier_status_shared': []
        }

        # Extract PRS scores
        prs_scores = {}
        for member, risks in individual_risks.items():
            if 'polygenic_risk_scores' in risks:
                prs_scores[member] = risks['polygenic_risk_scores']

        # Find shared high PRS
        diseases = set()
        for member_scores in prs_scores.values():
            diseases.update(member_scores.keys())

        for disease in diseases:
            high_risk_members = []
            for member, scores in prs_scores.items():
                if disease in scores and scores[disease].get('percentile', 0) > 75:
                    high_risk_members.append(member)

            if len(high_risk_members) > 1:
                shared_risks['high_prs_shared'].append({
                    'disease': disease,
                    'members': high_risk_members
                })

        # Shared clinical risks
        clinical_risks = {}
        for member, risks in individual_risks.items():
            if 'clinical_risk_screening' in risks:
                clinical_risks[member] = risks['clinical_risk_screening']

        # Find overlapping risk variants
        all_variants = set()
        for risks in clinical_risks.values():
            for category, variants in risks.items():
                if isinstance(variants, dict):
                    all_variants.update(variants.keys())

        for variant in all_variants:
            affected_members = []
            for member, risks in clinical_risks.items():
                for category, variants in risks.items():
                    if isinstance(variants, dict) and variant in variants:
                        affected_members.append(member)
                        break

            if len(affected_members) > 1:
                shared_risks['clinical_risks_shared'].append({
                    'variant': variant,
                    'members': affected_members
                })

        logger.info(f"Shared risks aggregation completed: {len(shared_risks['high_prs_shared'])} shared high PRS, {len(shared_risks['clinical_risks_shared'])} shared clinical risks")
        logger.info(f"Shared risks results: {shared_risks}")
        return shared_risks

    def detect_uniparental_disomy(self, chromosome_regions: Dict[str, List[Tuple[int, int]]]) -> Dict[str, List[Dict]]:
        """
        Detect large blocks of SNPs showing uniparental disomy patterns.

        Args:
            chromosome_regions: Dict with chr as keys, list of (start, end) positions

        Returns:
            Dict with potential UPD regions
        """
        logger.info(f"Detecting uniparental disomy in {len(chromosome_regions)} chromosome regions")
        upd_regions = {}

        # This is a simplified implementation
        # In practice, would need phased data and proper genomic coordinates
        # Here we simulate by looking for long runs of SNPs where child matches one parent perfectly

        for chr_name, regions in chromosome_regions.items():
            logger.debug(f"Analyzing UPD for chromosome {chr_name} with {len(regions)} regions")
            chr_snps = [snp for snp in self.common_snps if snp.startswith(f'rs') and f'chr{chr_name}' in snp]  # Placeholder

            for start_pos, end_pos in regions:
                # Get SNPs in this region (simplified)
                region_snps = chr_snps[:100]  # Placeholder

                if len(region_snps) < 10:
                    continue

                # Check if child matches mother perfectly in this region
                if self.mother_df is not None:
                    maternal_matches = 0
                    total = 0
                    for snp in region_snps:
                        if snp in self.child_df.index and snp in self.mother_df.index:
                            if self.child_df.loc[snp, 'genotype'] == self.mother_df.loc[snp, 'genotype']:
                                maternal_matches += 1
                            total += 1

                    if total > 0 and maternal_matches / total > 0.95:
                        upd_regions.setdefault(chr_name, []).append({
                            'start': start_pos,
                            'end': end_pos,
                            'type': 'maternal_UPD',
                            'confidence': maternal_matches / total
                        })

                # Same for paternal
                if self.father_df is not None:
                    paternal_matches = 0
                    total = 0
                    for snp in region_snps:
                        if snp in self.child_df.index and snp in self.father_df.index:
                            if self.child_df.loc[snp, 'genotype'] == self.father_df.loc[snp, 'genotype']:
                                paternal_matches += 1
                            total += 1

                    if total > 0 and paternal_matches / total > 0.95:
                        upd_regions.setdefault(chr_name, []).append({
                            'start': start_pos,
                            'end': end_pos,
                            'type': 'paternal_UPD',
                            'confidence': paternal_matches / total
                        })

        logger.info(f"Uniparental disomy detection completed: found UPD regions in {len(upd_regions)} chromosomes")
        logger.info(f"Uniparental disomy results: {upd_regions}")
        return upd_regions

    def enhanced_relationship_verification(self) -> Dict:
        """
        Enhanced relationship verification with detailed IBS analysis and confidence scores.
        """
        logger.info("Performing enhanced relationship verification")
        results = {}

        # Basic pairwise analyses
        if self.mother_df is not None:
            logger.debug("Analyzing child-mother relationship")
            analyzer_cm = FamilyAnalyzer(self.child_df, self.mother_df, "Child", "Mother")
            ibs_cm = analyzer_cm.calculate_identity_by_state()
            relationship_cm = analyzer_cm.predict_relationship(ibs_cm)
            mendelian_cm = analyzer_cm.analyze_mendelian_errors()

            results['child_mother'] = {
                'ibs_score': ibs_cm,
                'predicted_relationship': relationship_cm,
                'mendelian_errors': mendelian_cm,
                'confidence_score': self._calculate_relationship_confidence(ibs_cm, mendelian_cm)
            }

        if self.father_df is not None:
            logger.debug("Analyzing child-father relationship")
            analyzer_cf = FamilyAnalyzer(self.child_df, self.father_df, "Child", "Father")
            ibs_cf = analyzer_cf.calculate_identity_by_state()
            relationship_cf = analyzer_cf.predict_relationship(ibs_cf)
            mendelian_cf = analyzer_cf.analyze_mendelian_errors()

            results['child_father'] = {
                'ibs_score': ibs_cf,
                'predicted_relationship': relationship_cf,
                'mendelian_errors': mendelian_cf,
                'confidence_score': self._calculate_relationship_confidence(ibs_cf, mendelian_cf)
            }

        if self.mother_df is not None and self.father_df is not None:
            logger.debug("Analyzing mother-father relationship")
            analyzer_mf = FamilyAnalyzer(self.mother_df, self.father_df, "Mother", "Father")
            ibs_mf = analyzer_mf.calculate_identity_by_state()
            relationship_mf = analyzer_mf.predict_relationship(ibs_mf)

            results['mother_father'] = {
                'ibs_score': ibs_mf,
                'predicted_relationship': relationship_mf,
                'relationship_type': 'unrelated' if ibs_mf < 0.1 else 'related'
            }

        # Overall family configuration assessment
        family_config = self._assess_family_configuration(results)
        results['family_configuration'] = family_config

        logger.info("Relationship verification completed")
        logger.info(f"Relationship verification results: {results}")
        return results

    def _calculate_relationship_confidence(self, ibs_score: float, mendelian_errors: Dict) -> float:
        """Calculate confidence score for parent-child relationship."""
        error_rate = mendelian_errors.get('error_rate', 1.0)

        # High IBS and low error rate = high confidence
        confidence = (ibs_score * 0.7) + ((1 - error_rate) * 0.3)
        return min(confidence, 1.0)

    def _assess_family_configuration(self, relationship_results: Dict) -> Dict:
        """Assess overall family configuration based on relationships."""
        config = {
            'type': 'unknown',
            'confidence': 0.0,
            'issues': []
        }

        has_mother = 'child_mother' in relationship_results
        has_father = 'child_father' in relationship_results

        if has_mother and has_father:
            cm_conf = relationship_results['child_mother']['confidence_score']
            cf_conf = relationship_results['child_father']['confidence_score']

            if cm_conf > 0.8 and cf_conf > 0.8:
                config['type'] = 'trio'
                config['confidence'] = (cm_conf + cf_conf) / 2
            else:
                config['type'] = 'trio_with_issues'
                config['issues'].append('Low confidence in parent-child relationships')
        elif has_mother:
            conf = relationship_results['child_mother']['confidence_score']
            config['type'] = 'duo_maternal'
            config['confidence'] = conf
        elif has_father:
            conf = relationship_results['child_father']['confidence_score']
            config['type'] = 'duo_paternal'
            config['confidence'] = conf
        else:
            config['type'] = 'singleton'
            config['confidence'] = 0.5  # Neutral

        return config


def run_family_analyses(family_data: Dict[str, pd.DataFrame],
                        risk_variants: Optional[List[str]] = None,
                        gene_variants: Optional[Dict[str, List[str]]] = None,
                        chromosome_regions: Optional[Dict[str, List[Tuple[int, int]]]] = None,
                        individual_risks: Optional[Dict[str, Dict]] = None) -> Dict:
    """
    Main function to run all family analyses.

    Args:
        family_data: Dict with 'child', 'mother', 'father' DataFrames
        risk_variants: List of rsIDs for variant tracing
        gene_variants: Dict of genes to rsIDs for compound het detection
        chromosome_regions: Dict of chromosomes to regions for UPD detection
        individual_risks: Dict of individual risk analyses

    Returns:
        Dict with all family analysis results
    """
    logger.info("Starting family analyses")
    try:
        analyzer = AdvancedFamilyAnalyzer(family_data)

        results = {
            'relationship_verification': analyzer.enhanced_relationship_verification()
        }

        if risk_variants:
            results['variant_origins'] = analyzer.trace_variant_origins(risk_variants)

        if gene_variants:
            results['compound_heterozygosity'] = analyzer.detect_compound_heterozygosity(gene_variants)

        if individual_risks:
            results['shared_risks'] = analyzer.aggregate_shared_risks(individual_risks)

        if chromosome_regions:
            results['uniparental_disomy'] = analyzer.detect_uniparental_disomy(chromosome_regions)

        logger.info("Family analyses completed successfully")
        logger.info(f"Family analyses results summary: {results}")
        return results
    except Exception as e:
        logger.error(f"Error in family analyses: {e}", exc_info=True)
        raise
