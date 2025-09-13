# SNP data for various analyses

recessive_snps = {
    'rs113993960': {'gene': 'CFTR', 'condition': 'Cystic Fibrosis', 'risk_allele': 'T', 'interp': {'CT': 'Carrier', 'TT': 'Affected'}},
    'rs334': {'gene': 'HBB', 'condition': 'Sickle Cell Anemia', 'risk_allele': 'A', 'interp': {'GA': 'Carrier', 'AA': 'Affected'}}
}

cancer_snps = {
    'rs80357906': {'gene': 'BRCA1', 'risk': 'Hereditary Cancer Risk (185delAG)'},
    'rs80357713': {'gene': 'BRCA1', 'risk': 'Hereditary Cancer Risk (5382insC)'},
    'rs80359551': {'gene': 'BRCA2', 'risk': 'Hereditary Cancer Risk (6174delT)'},
    'rs63750247': {'gene': 'MSH2', 'risk': 'Lynch Syndrome (Colorectal Cancer Risk)'},
    'rs1447295': {'gene': '8q24 region', 'risk': 'Prostate Cancer'},
    'rs1805007': {'gene': 'MC1R', 'risk': 'Melanoma Skin Cancer (R151C)'},
    'rs1805008': {'gene': 'MC1R', 'risk': 'Melanoma Skin Cancer (R160W)'},
    'rs1042522': {'gene': 'TP53', 'risk': 'Li-Fraumeni Syndrome (Common Polymorphism)'},
    'rs121964876': {'gene': 'CDH1', 'risk': 'Hereditary Diffuse Gastric Cancer'},
    'rs74799832': {'gene': 'RET', 'risk': 'Multiple Endocrine Neoplasia Type 2'},
    'rs104893829': {'gene': 'VHL', 'risk': 'Von Hippel-Lindau Syndrome'},
    'rs749979841': {'gene': 'TSC1', 'risk': 'Tuberous Sclerosis Complex'},
    'rs28934872': {'gene': 'TSC2', 'risk': 'Tuberous Sclerosis Complex'},
}

cardiovascular_snps = {
    'rs121913579': {'gene': 'MYH7', 'risk': 'Hypertrophic Cardiomyopathy (p.Arg403Gln)'},
    'rs121907891': {'gene': 'MYBPC3', 'risk': 'Hypertrophic Cardiomyopathy (p.Arg502Trp)'},
    'rs72646899': {'gene': 'TTN', 'risk': 'Dilated Cardiomyopathy (truncating variant)'},
    'rs609320': {'gene': 'LMNA', 'risk': 'Dilated Cardiomyopathy (p.Arg482Gln)'},
    'rs121912765': {'gene': 'PKP2', 'risk': 'Arrhythmogenic Right Ventricular Cardiomyopathy'},
    'rs121912768': {'gene': 'DSP', 'risk': 'Arrhythmogenic Right Ventricular Cardiomyopathy'},
    'rs121912773': {'gene': 'DSG2', 'risk': 'Arrhythmogenic Right Ventricular Cardiomyopathy'},
    'rs120074178': {'gene': 'KCNQ1', 'risk': 'Long QT Syndrome (p.Gly269Asp)'},
    'rs120074179': {'gene': 'KCNH2', 'risk': 'Long QT Syndrome (p.Arg176Trp)'},
    'rs7626962': {'gene': 'SCN5A', 'risk': 'Brugada Syndrome (p.Arg1193Gln)'},
    'rs137854600': {'gene': 'FBN1', 'risk': 'Marfan Syndrome (p.Cys1663Arg)'},
    'rs113994087': {'gene': 'COL3A1', 'risk': 'Vascular Ehlers-Danlos Syndrome (p.Gly661Arg)'},
    'rs1122608': {'gene': 'LDLR', 'risk': 'Familial Hypercholesterolemia (p.Asp266Asn)'},
    'rs5742904': {'gene': 'APOB', 'risk': 'Familial Hypercholesterolemia (p.Arg3500Gln)'},
    'rs11591147': {'gene': 'PCSK9', 'risk': 'Familial Hypercholesterolemia (p.Asp374Tyr)'}
}

neuro_snps = {
    'rs34637584': {'gene': 'LRRK2', 'risk': 'Parkinson\'s Disease (p.Gly2019Ser)'},
    'rs76763715': {'gene': 'GBA', 'risk': 'Parkinson\'s Disease (p.Asn370Ser)'},
    'rs1061170': {'gene': 'CFH', 'risk': 'Age-Related Macular Degeneration (p.Tyr402His)'},
    'rs28929474': {'gene': 'SERPINA1', 'risk': 'Alpha-1 Antitrypsin Deficiency (p.Glu342Lys)'}
}

mito_snps = {
    'rs199476118': {'gene': 'MT-ND1', 'risk': 'Leber\'s Hereditary Optic Neuropathy (m.3460G>A)'},
    'rs199476112': {'gene': 'MT-ND4', 'risk': 'Leber\'s Hereditary Optic Neuropathy (m.11778G>A)'},
    'rs199476104': {'gene': 'MT-ND6', 'risk': 'Leber\'s Hereditary Optic Neuropathy (m.14484T>C)'},
    'rs199474657': {'gene': 'MT-TL1', 'risk': 'Mitochondrial Encephalomyopathy (MELAS, m.3243A>G)'}
}

protective_snps = {
    'rs671': {'gene': 'ALDH2', 'trait': 'Alcohol Flush Protection', 'protective_allele': 'A', 'interp': {'GA': 'Reduced Alcohol Tolerance', 'AA': 'Strongly Reduced Alcohol Tolerance'}},
    'rs1229984': {'gene': 'ADH1B', 'trait': 'Alcoholism Protection', 'protective_allele': 'A', 'interp': {'GA': 'Reduced Alcoholism Risk', 'AA': 'Strongly Reduced Alcoholism Risk'}}
}

ancestry_panels = {
    "Ashkenazi Jewish": {
        'rs387906309': {'gene': 'HEXA', 'condition': 'Tay-Sachs Disease'},
        'rs28940279': {'gene': 'ASPA', 'condition': 'Canavan Disease'},
        'rs111033171': {'gene': 'IKBKAP', 'condition': 'Familial Dysautonomia'},
        'rs113993962': {'gene': 'BLM', 'condition': 'Bloom Syndrome'},
    },
    "Northern European": {
        'rs1800562': {'gene': 'HFE', 'condition': 'Hereditary Hemochromatosis (C282Y)'},
        'rs1799945': {'gene': 'HFE', 'condition': 'Hereditary Hemochromatosis (H63D)'},
    },
    "Mediterranean/South Asian": {
        'rs334': {'gene': 'HBB', 'condition': 'Beta-thalassemia (p.Glu7Val)'},
        'rs33930165': {'gene': 'HBB', 'condition': 'Beta-thalassemia (p.Glu7Lys)'},
        'rs33950507': {'gene': 'HBB', 'condition': 'Beta-thalassemia (p.Glu27Lys)'},
    },
    "Southeast Asian": {
        'rs4149056': {'gene': 'SLCO1B1', 'condition': 'Statin-induced myopathy risk'},
        'rs671': {'gene': 'ALDH2', 'condition': 'Alcohol intolerance'},
    },
    "African Ancestry": {
        'rs334': {'gene': 'HBB', 'condition': 'Sickle Cell Disease'},
        'rs113993960': {'gene': 'CFTR', 'condition': 'Cystic Fibrosis (less common)'},
    },
    "Hispanic/Latino": {
        'rs1800562': {'gene': 'HFE', 'condition': 'Hereditary Hemochromatosis'},
        'rs11591147': {'gene': 'PCSK9', 'condition': 'Familial Hypercholesterolemia'},
    }
}

acmg_sf_variants = {
    'rs80357713': {'gene': 'BRCA1', 'condition': 'Hereditary Breast and Ovarian Cancer'},
    'rs80359551': {'gene': 'BRCA2', 'condition': 'Hereditary Breast and Ovarian Cancer'},
    'rs121913579': {'gene': 'MYH7', 'condition': 'Hypertrophic Cardiomyopathy'},
    'rs121907891': {'gene': 'MYBPC3', 'condition': 'Hypertrophic Cardiomyopathy'},
    'rs72646899': {'gene': 'TTN', 'condition': 'Dilated Cardiomyopathy'},
    'rs609320': {'gene': 'LMNA', 'condition': 'Dilated Cardiomyopathy'},
    'rs121912765': {'gene': 'PKP2', 'condition': 'Arrhythmogenic Right Ventricular Cardiomyopathy'},
    'rs120074178': {'gene': 'KCNQ1', 'condition': 'Long QT Syndrome'},
    'rs120074179': {'gene': 'KCNH2', 'condition': 'Long QT Syndrome'},
    'rs7626962': {'gene': 'SCN5A', 'condition': 'Brugada Syndrome'},
    'rs137854600': {'gene': 'FBN1', 'condition': 'Marfan Syndrome'},
    'rs113994087': {'gene': 'COL3A1', 'condition': 'Vascular Ehlers-Danlos Syndrome'},
    'rs1122608': {'gene': 'LDLR', 'condition': 'Familial Hypercholesterolemia'},
    'rs5742904': {'gene': 'APOB', 'condition': 'Familial Hypercholesterolemia'},
    'rs11591147': {'gene': 'PCSK9', 'condition': 'Familial Hypercholesterolemia'},
    'rs199476118': {'gene': 'MT-ND1', 'condition': 'Leber Hereditary Optic Neuropathy'},
    'rs199476112': {'gene': 'MT-ND4', 'condition': 'Leber Hereditary Optic Neuropathy'},
    'rs199476104': {'gene': 'MT-ND6', 'condition': 'Leber Hereditary Optic Neuropathy'},
    'rs199474657': {'gene': 'MT-TL1', 'condition': 'Mitochondrial Encephalomyopathy'},
    'rs63750247': {'gene': 'MSH2', 'condition': 'Lynch Syndrome'},
    'rs267607880': {'gene': 'MSH6', 'condition': 'Lynch Syndrome'},
    'rs63751147': {'gene': 'MLH1', 'condition': 'Lynch Syndrome'},
    'rs63750943': {'gene': 'PMS2', 'condition': 'Lynch Syndrome'},
    'rs41307846': {'gene': 'APC', 'condition': 'Familial Adenomatous Polyposis'},
    'rs180177104': {'gene': 'BMPR1A', 'condition': 'Juvenile Polyposis Syndrome'},
    'rs41310927': {'gene': 'SMAD4', 'condition': 'Juvenile Polyposis Syndrome'},
    'rs121434592': {'gene': 'PTEN', 'condition': 'PTEN Hamartoma Tumor Syndrome / Cowden Syndrome'},
    'rs587782044': {'gene': 'TP53', 'condition': 'Li-Fraumeni Syndrome'},
    'rs121913333': {'gene': 'WT1', 'condition': 'Wilms Tumor'},
    'rs121912651': {'gene': 'NF2', 'condition': 'Neurofibromatosis Type 2'},
    'rs80338902': {'gene': 'PALB2', 'condition': 'Fanconi Anemia'},
    'rs121913279': {'gene': 'BRIP1/NBN', 'condition': 'Fanconi Anemia / Nijmegen Breakage Syndrome'},
    'rs200796965': {'gene': 'RAD51C/RAD51D', 'condition': 'Fanconi Anemia'},
    'rs80358971': {'gene': 'FANCI/FANCD2/FANCG/FANCA/FANCC/FANCE/FANCF/BRCA1/BRCA2/RAD51/ATM', 'condition': 'Fanconi Anemia / Ataxia-Telangiectasia'},
    'rs80358971': {'gene': 'FANCM', 'condition': 'Fanconi Anemia'},
    'rs80358971': {'gene': 'SLX4', 'condition': 'Fanconi Anemia'},
    'rs80358971': {'gene': 'ERCC4', 'condition': 'Fanconi Anemia'},
    'rs121908745': {'gene': 'RYR1', 'condition': 'Malignant Hyperthermia'},
    'rs118192178': {'gene': 'RYR1', 'condition': 'Malignant Hyperthermia'},
    'rs121964876': {'gene': 'CDH1', 'condition': 'Hereditary Diffuse Gastric Cancer'},
    'rs74799832': {'gene': 'RET', 'condition': 'Multiple Endocrine Neoplasia Type 2'},
    'rs104893829': {'gene': 'VHL', 'condition': 'Von Hippel-Lindau Syndrome'},
    'rs749979841': {'gene': 'TSC1', 'condition': 'Tuberous Sclerosis Complex'},
    'rs28934872': {'gene': 'TSC2', 'condition': 'Tuberous Sclerosis Complex'},
    'rs1061170': {'gene': 'CFH', 'condition': 'Age-Related Macular Degeneration'},
    'rs28929474': {'gene': 'SERPINA1', 'condition': 'Alpha-1 Antitrypsin Deficiency'},
    'rs45517242': {'gene': 'RB1', 'condition': 'Retinoblastoma'},
    'rs121913591': {'gene': 'SDHB', 'condition': 'Paraganglioma and Pheochromocytoma'},
    'rs121913595': {'gene': 'SDHD', 'condition': 'Paraganglioma and Pheochromocytoma'},
    'rs80338793': {'gene': 'SDHC', 'condition': 'Paraganglioma and Pheochromocytoma'},
    'rs80338797': {'gene': 'SDHAF2', 'condition': 'Paraganglioma and Pheochromocytoma'},
    'rs121918579': {'gene': 'MAX', 'condition': 'Paraganglioma and Pheochromocytoma'},
    'rs121918580': {'gene': 'TMEM127', 'condition': 'Paraganglioma and Pheochromocytoma'},
    'rs879255283': {'gene': 'MEN1', 'condition': 'Multiple Endocrine Neoplasia Type 1'},
}

pgx_snps = {
    'rs4244285': {'gene': 'CYP2C19', 'relevance': 'Clopidogrel Metabolism', 'interp': {'GG': 'Normal Metabolizer', 'AG': 'Intermediate', 'AA': 'Poor'}},
    'rs1057910': {'gene': 'CYP2C9*2', 'relevance': 'Warfarin/NSAID Metabolism', 'interp': {'CC': 'Normal', 'CT': 'Intermediate', 'TT': 'Poor'}},
    'rs1799853': {'gene': 'CYP2C9*3', 'relevance': 'Warfarin/NSAID Metabolism', 'interp': {'AA': 'Normal', 'AC': 'Intermediate', 'CC': 'Poor'}},
    'rs9923231': {'gene': 'VKORC1', 'relevance': 'Warfarin Sensitivity', 'interp': {'GG': 'Normal sensitivity', 'AG': 'Increased', 'AA': 'High'}},
    'rs1800460': {'gene': 'UGT1A1', 'relevance': 'Irinotecan (Chemo) Toxicity', 'interp': {'GG': 'Normal', 'AG': 'Increased risk', 'AA': 'High risk'}},
    'rs3892097': {'gene': 'CYP2D6', 'relevance': 'SSRIs/Opioids Metabolism', 'interp': {'GG': 'Normal', 'AG': 'Intermediate', 'AA': 'Poor'}},
    'rs1800462': {'gene': 'TPMT', 'relevance': 'Thiopurine Metabolism', 'interp': {'GG': 'Normal', 'AG': 'Intermediate', 'AA': 'Poor'}},
    'rs55886062': {'gene': 'DPYD', 'relevance': 'Fluoropyrimidine Toxicity', 'interp': {'CC': 'Normal', 'CT': 'Intermediate', 'TT': 'Poor'}},
    'rs12248560': {'gene': 'CYP2C19', 'relevance': 'Proton Pump Inhibitors (PPIs)', 'interp': {'CC': 'Normal', 'CT': 'Intermediate', 'TT': 'Poor'}},
    'rs28399504': {'gene': 'CYP2C19', 'relevance': 'Antidepressants (e.g., Citalopram)', 'interp': {'GG': 'Normal', 'AG': 'Intermediate', 'AA': 'Poor'}},
    'rs776746': {'gene': 'CYP3A5', 'relevance': 'Tacrolimus/Immunosuppressants', 'interp': {'CC': 'Poor', 'CT': 'Intermediate', 'TT': 'Normal'}},
    'rs4149056': {'gene': 'SLCO1B1', 'relevance': 'Statins (e.g., Simvastatin)', 'interp': {'TT': 'Normal', 'CT': 'Intermediate', 'CC': 'Poor'}}
}

# Star allele definitions for comprehensive PGx analysis
star_allele_definitions = {
    'CYP2C19': {
        '*1': {'haplotypes': [], 'function': 'Normal', 'description': 'Reference haplotype'},
        '*2': {'haplotypes': ['rs4244285:A'], 'function': 'No function', 'description': '681G>A'},
        '*3': {'haplotypes': ['rs4986893:A'], 'function': 'No function', 'description': '636G>A'},
        '*17': {'haplotypes': ['rs12248560:T'], 'function': 'Increased function', 'description': '-806C>T'},
        '*4': {'haplotypes': ['rs28399504:A'], 'function': 'No function', 'description': '1A>C'},
        '*5': {'haplotypes': ['rs56337013:C'], 'function': 'No function', 'description': '1297C>T'},
        '*6': {'haplotypes': ['rs72552267:A'], 'function': 'No function', 'description': '395G>A'},
        '*7': {'haplotypes': ['rs72558186:A'], 'function': 'No function', 'description': '19294T>A'},
        '*8': {'haplotypes': ['rs41291556:T'], 'function': 'No function', 'description': '358T>C'},
        '*9': {'haplotypes': ['rs17884712:G'], 'function': 'No function', 'description': '431G>A'},
        '*10': {'haplotypes': ['rs6413438:T'], 'function': 'No function', 'description': '680C>T'},
    },
    'CYP2D6': {
        '*1': {'haplotypes': [], 'function': 'Normal', 'description': 'Reference haplotype'},
        '*3': {'haplotypes': ['rs35742686:delA'], 'function': 'No function', 'description': '2549delA'},
        '*4': {'haplotypes': ['rs3892097:A', 'rs1065852:T', 'rs28371725:C'], 'function': 'No function', 'description': '1846G>A + 100C>T + 4180G>C'},
        '*5': {'haplotypes': ['deletion'], 'function': 'No function', 'description': 'Gene deletion'},
        '*6': {'haplotypes': ['rs5030655:delT', 'rs3892097:A'], 'function': 'No function', 'description': '1707delT + 1846G>A'},
        '*10': {'haplotypes': ['rs1065852:T', 'rs1135840:C'], 'function': 'Decreased function', 'description': '100C>T + 1661G>C'},
        '*17': {'haplotypes': ['rs28371706:T', 'rs16947:T', 'rs28371725:C'], 'function': 'Decreased function', 'description': '1023C>T + 886C>T + 4180G>C'},
        '*41': {'haplotypes': ['rs28371725:C', 'rs16947:T', 'rs267608319:T'], 'function': 'Decreased function', 'description': '4180G>C + 886C>T + 2988G>A'},
    },
    'CYP2C9': {
        '*1': {'haplotypes': [], 'function': 'Normal', 'description': 'Reference haplotype'},
        '*2': {'haplotypes': ['rs1799853:C'], 'function': 'Decreased function', 'description': '430C>T'},
        '*3': {'haplotypes': ['rs1057910:A'], 'function': 'Decreased function', 'description': '1075A>C'},
    },
    'TPMT': {
        '*1': {'haplotypes': [], 'function': 'Normal', 'description': 'Reference haplotype'},
        '*2': {'haplotypes': ['rs1800462:A'], 'function': 'No function', 'description': '238G>C'},
        '*3A': {'haplotypes': ['rs1800460:A', 'rs1142345:T'], 'function': 'No function', 'description': '460G>A + 719A>G'},
        '*3B': {'haplotypes': ['rs1800460:A'], 'function': 'No function', 'description': '460G>A'},
        '*3C': {'haplotypes': ['rs1142345:T'], 'function': 'No function', 'description': '719A>G'},
    },
    'DPYD': {
        '*1': {'haplotypes': [], 'function': 'Normal', 'description': 'Reference haplotype'},
        '*2A': {'haplotypes': ['rs3918290:T'], 'function': 'No function', 'description': '1905+1G>A'},
        '*13': {'haplotypes': ['rs55886062:A'], 'function': 'Decreased function', 'description': '1679T>G'},
    }
}

# CPIC dosing guidelines
cpic_guidelines = {
    'CYP2C19': {
        'clopidogrel': {
            'Poor': 'Avoid clopidogrel due to lack of efficacy; use alternative antiplatelet therapy (e.g., ticagrelor, prasugrel)',
            'Intermediate': 'Standard dose with platelet function testing',
            'Normal': 'Standard dose',
            'Rapid': 'Standard dose',
            'Ultrarapid': 'Standard dose'
        },
        'citalopram': {
            'Poor': 'Reduce dose by 50%',
            'Intermediate': 'Use with caution',
            'Normal': 'Standard dose',
            'Rapid': 'Standard dose',
            'Ultrarapid': 'Standard dose'
        }
    },
    'CYP2D6': {
        'codeine': {
            'Poor': 'Avoid use',
            'Intermediate': 'Use with caution',
            'Normal': 'Standard dose',
            'Rapid': 'Standard dose',
            'Ultrarapid': 'Avoid use - risk of toxicity'
        },
        'tamoxifen': {
            'Poor': 'Alternative therapy',
            'Intermediate': 'Alternative therapy',
            'Normal': 'Standard dose',
            'Rapid': 'Standard dose',
            'Ultrarapid': 'Standard dose'
        }
    },
    'CYP2C9': {
        'warfarin': {
            'Poor': 'Reduce initial dose by 30-50%',
            'Intermediate': 'Reduce initial dose by 20-30%',
            'Normal': 'Standard dose',
            'Rapid': 'Standard dose',
            'Ultrarapid': 'Standard dose'
        }
    },
    'TPMT': {
        'azathioprine': {
            'Poor': 'Reduce dose by 90%',
            'Intermediate': 'Reduce dose by 50%',
            'Normal': 'Standard dose',
            'Rapid': 'Standard dose',
            'Ultrarapid': 'Standard dose'
        }
    },
    'DPYD': {
        'fluorouracil': {
            'Poor': 'Avoid use or reduce dose by 50%',
            'Intermediate': 'Reduce dose by 25%',
            'Normal': 'Standard dose',
            'Rapid': 'Standard dose',
            'Ultrarapid': 'Standard dose'
        }
    }
}

adverse_reaction_snps = {
    'rs4149056': {'gene': 'SLCO1B1', 'relevance': 'Simvastatin Myopathy Risk', 'interp': {'TT': 'Normal risk', 'CT': 'Increased risk', 'CC': 'High risk'}},
    'rs3918290': {'gene': 'HLA-B*15:02', 'relevance': 'Carbamazepine SJS Risk', 'interp': {'GG': 'Normal', 'GT': 'Significantly Increased Risk', 'TT': 'Significantly Increased Risk'}},
    'rs144488907': {'gene': 'HLA-B*58:01', 'relevance': 'Allopurinol SJS/TEN Risk', 'interp': {'AA': 'Normal', 'AT': 'Carrier', 'TT': 'At risk'}},
    'rs1061235': {'gene': 'HLA-A*31:01', 'relevance': 'Carbamazepine SJS Risk', 'interp': {'GG': 'Normal', 'GA': 'Carrier', 'AA': 'At risk'}}
}

# Legacy PRS models for backward compatibility
legacy_prs_models = {
    "Coronary Artery Disease": {'rsid': ['rs10757274', 'rs10757278', 'rs1333049', 'rs2383206'], 'effect_allele': ['G', 'G', 'C', 'A'], 'effect_weight': [0.177, 0.198, 0.126, 0.106]},
    "Type 2 Diabetes": {'rsid': ['rs7903146', 'rs13266634', 'rs7754840', 'rs10811661', 'rs4506565'], 'effect_allele': ['T', 'C', 'C', 'T', 'T'], 'effect_weight': [0.31, 0.14, 0.11, 0.22, 0.12]},
    "Atrial Fibrillation": {'rsid': ['rs2200733', 'rs10033464', 'rs6817105'], 'effect_allele': ['T', 'T', 'C'], 'effect_weight': [0.45, 0.30, 0.22]},
    "Colorectal Cancer": {'rsid': ['rs6983267', 'rs4939827', 'rs10795668'], 'effect_allele': ['G', 'C', 'G'], 'effect_weight': [0.15, 0.14, 0.09]},
    "Prostate Cancer": {'rsid': ['rs1447295', 'rs6983267'], 'effect_allele': ['A', 'G'], 'effect_weight': [0.30, 0.25]},
    "Ischemic Stroke": {'rsid': ['rs12425791', 'rs11833579', 'rs2200733'], 'effect_allele': ['A', 'A', 'T'], 'effect_weight': [0.18, 0.15, 0.28]},
    "Inflammatory Bowel Disease": {'rsid': ['rs2066844', 'rs2476601', 'rs2187668'], 'effect_allele': ['G', 'A', 'T'], 'effect_weight': [0.25, 0.20, 0.15]},
    "Rheumatoid Arthritis": {'rsid': ['rs2476601', 'rs3087243'], 'effect_allele': ['A', 'G'], 'effect_weight': [0.30, 0.15]},
    "Systemic Lupus Erythematosus": {'rsid': ['rs2476601', 'rs7574865'], 'effect_allele': ['A', 'T'], 'effect_weight': [0.28, 0.18]},
    "Multiple Sclerosis": {'rsid': ['rs9271366', 'rs340874'], 'effect_allele': ['C', 'C'], 'effect_weight': [0.22, 0.19]},
    "Celiac Disease": {'rsid': ['rs2187668', 'rs3184504'], 'effect_allele': ['T', 'A'], 'effect_weight': [0.20, 0.17]},
    "Major Depressive Disorder": {'rsid': ['rs10503253', 'rs35936514'], 'effect_allele': ['A', 'C'], 'effect_weight': [0.15, 0.12]},
    "Schizophrenia": {'rsid': ['rs1625579', 'rs7004633'], 'effect_allele': ['T', 'C'], 'effect_weight': [0.18, 0.14]},
    "Osteoporosis": {'rsid': ['rs3736228', 'rs2941740'], 'effect_allele': ['T', 'A'], 'effect_weight': [0.20, 0.15]},
    "Asthma": {'rsid': ['rs2305480', 'rs4950928'], 'effect_allele': ['G', 'C'], 'effect_weight': [0.18, 0.22]}
}

# Genome-wide PRS Models with PGS Catalog Integration
prs_models = {
    # Cardiometabolic Diseases
    "Coronary Artery Disease": {
        'simple_model': {
            'rsid': ['rs10757274', 'rs10757278', 'rs1333049', 'rs2383206'],
            'effect_allele': ['G', 'G', 'C', 'A'],
            'effect_weight': [0.177, 0.198, 0.126, 0.106]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000018', 'description': 'CAD metaGRS'},
            {'pgs_id': 'PGS000012', 'description': 'CAD GWAS'},
            {'pgs_id': 'PGS000013', 'description': 'CAD multi-ancestry'}
        ],
        'category': 'Cardiometabolic',
        'description': 'Risk of coronary artery disease based on genetic variants'
    },

    "Type 2 Diabetes": {
        'simple_model': {
            'rsid': ['rs7903146', 'rs13266634', 'rs7754840', 'rs10811661', 'rs4506565'],
            'effect_allele': ['T', 'C', 'C', 'T', 'T'],
            'effect_weight': [0.31, 0.14, 0.11, 0.22, 0.12]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000014', 'description': 'T2D meta-analysis'},
            {'pgs_id': 'PGS000015', 'description': 'T2D European ancestry'},
            {'pgs_id': 'PGS000016', 'description': 'T2D multi-ethnic'}
        ],
        'category': 'Cardiometabolic',
        'description': 'Risk of type 2 diabetes mellitus'
    },

    "Atrial Fibrillation": {
        'simple_model': {
            'rsid': ['rs2200733', 'rs10033464', 'rs6817105'],
            'effect_allele': ['T', 'T', 'C'],
            'effect_weight': [0.45, 0.30, 0.22]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000017', 'description': 'AF GWAS meta-analysis'}
        ],
        'category': 'Cardiometabolic',
        'description': 'Risk of atrial fibrillation'
    },

    "Hypertension": {
        'genomewide_models': [
            {'pgs_id': 'PGS000019', 'description': 'Hypertension GWAS'},
            {'pgs_id': 'PGS000020', 'description': 'Blood pressure traits'}
        ],
        'category': 'Cardiometabolic',
        'description': 'Risk of essential hypertension'
    },

    "Ischemic Stroke": {
        'simple_model': {
            'rsid': ['rs12425791', 'rs11833579', 'rs2200733'],
            'effect_allele': ['A', 'A', 'T'],
            'effect_weight': [0.18, 0.15, 0.28]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000021', 'description': 'Ischemic stroke GWAS'}
        ],
        'category': 'Cardiometabolic',
        'description': 'Risk of ischemic stroke'
    },

    # Cancer Risks
    "Prostate Cancer": {
        'simple_model': {
            'rsid': ['rs1447295', 'rs6983267'],
            'effect_allele': ['A', 'G'],
            'effect_weight': [0.30, 0.25]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000022', 'description': 'Prostate cancer GWAS'},
            {'pgs_id': 'PGS000023', 'description': 'Prostate cancer risk score'}
        ],
        'category': 'Cancer',
        'description': 'Risk of prostate cancer'
    },

    "Breast Cancer": {
        'genomewide_models': [
            {'pgs_id': 'PGS000024', 'description': 'Breast cancer GWAS'},
            {'pgs_id': 'PGS000025', 'description': 'Breast cancer polygenic risk'}
        ],
        'category': 'Cancer',
        'description': 'Risk of breast cancer'
    },

    "Colorectal Cancer": {
        'simple_model': {
            'rsid': ['rs6983267', 'rs4939827', 'rs10795668'],
            'effect_allele': ['G', 'C', 'G'],
            'effect_weight': [0.15, 0.14, 0.09]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000026', 'description': 'Colorectal cancer GWAS'}
        ],
        'category': 'Cancer',
        'description': 'Risk of colorectal cancer'
    },

    "Melanoma": {
        'genomewide_models': [
            {'pgs_id': 'PGS000027', 'description': 'Melanoma GWAS'}
        ],
        'category': 'Cancer',
        'description': 'Risk of cutaneous melanoma'
    },

    # Autoimmune and Inflammatory Conditions
    "Inflammatory Bowel Disease": {
        'simple_model': {
            'rsid': ['rs2066844', 'rs2476601', 'rs2187668'],
            'effect_allele': ['G', 'A', 'T'],
            'effect_weight': [0.25, 0.20, 0.15]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000028', 'description': 'IBD GWAS meta-analysis'},
            {'pgs_id': 'PGS000029', 'description': 'Crohn\'s disease specific'},
            {'pgs_id': 'PGS000030', 'description': 'Ulcerative colitis specific'}
        ],
        'category': 'Autoimmune',
        'description': 'Risk of inflammatory bowel disease (Crohn\'s/UC)'
    },

    "Rheumatoid Arthritis": {
        'simple_model': {
            'rsid': ['rs2476601', 'rs3087243'],
            'effect_allele': ['A', 'G'],
            'effect_weight': [0.30, 0.15]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000031', 'description': 'RA GWAS meta-analysis'}
        ],
        'category': 'Autoimmune',
        'description': 'Risk of rheumatoid arthritis'
    },

    "Systemic Lupus Erythematosus": {
        'simple_model': {
            'rsid': ['rs2476601', 'rs7574865'],
            'effect_allele': ['A', 'T'],
            'effect_weight': [0.28, 0.18]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000032', 'description': 'SLE GWAS'}
        ],
        'category': 'Autoimmune',
        'description': 'Risk of systemic lupus erythematosus'
    },

    "Multiple Sclerosis": {
        'simple_model': {
            'rsid': ['rs9271366', 'rs340874'],
            'effect_allele': ['C', 'C'],
            'effect_weight': [0.22, 0.19]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000033', 'description': 'MS GWAS meta-analysis'}
        ],
        'category': 'Autoimmune',
        'description': 'Risk of multiple sclerosis'
    },

    "Celiac Disease": {
        'simple_model': {
            'rsid': ['rs2187668', 'rs3184504'],
            'effect_allele': ['T', 'A'],
            'effect_weight': [0.20, 0.17]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000034', 'description': 'Celiac disease GWAS'}
        ],
        'category': 'Autoimmune',
        'description': 'Risk of celiac disease'
    },

    # Mental Health Conditions
    "Major Depressive Disorder": {
        'simple_model': {
            'rsid': ['rs10503253', 'rs35936514'],
            'effect_allele': ['A', 'C'],
            'effect_weight': [0.15, 0.12]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000035', 'description': 'MDD GWAS meta-analysis'}
        ],
        'category': 'Mental Health',
        'description': 'Risk of major depressive disorder'
    },

    "Bipolar Disorder": {
        'genomewide_models': [
            {'pgs_id': 'PGS000036', 'description': 'Bipolar disorder GWAS'}
        ],
        'category': 'Mental Health',
        'description': 'Risk of bipolar disorder'
    },

    "Schizophrenia": {
        'simple_model': {
            'rsid': ['rs1625579', 'rs7004633'],
            'effect_allele': ['T', 'C'],
            'effect_weight': [0.18, 0.14]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000037', 'description': 'Schizophrenia GWAS meta-analysis'}
        ],
        'category': 'Mental Health',
        'description': 'Risk of schizophrenia'
    },

    "ADHD": {
        'genomewide_models': [
            {'pgs_id': 'PGS000038', 'description': 'ADHD GWAS'}
        ],
        'category': 'Mental Health',
        'description': 'Risk of attention deficit hyperactivity disorder'
    },

    # Skeletal and Other Conditions
    "Osteoporosis": {
        'simple_model': {
            'rsid': ['rs3736228', 'rs2941740'],
            'effect_allele': ['T', 'A'],
            'effect_weight': [0.20, 0.15]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000039', 'description': 'Bone mineral density GWAS'},
            {'pgs_id': 'PGS000040', 'description': 'Osteoporotic fracture risk'}
        ],
        'category': 'Skeletal',
        'description': 'Risk of osteoporosis and bone mineral density reduction'
    },

    "Asthma": {
        'simple_model': {
            'rsid': ['rs2305480', 'rs4950928'],
            'effect_allele': ['G', 'C'],
            'effect_weight': [0.18, 0.22]
        },
        'genomewide_models': [
            {'pgs_id': 'PGS000041', 'description': 'Asthma GWAS meta-analysis'}
        ],
        'category': 'Skeletal',
        'description': 'Risk of asthma'
    }
}

# Helper functions for PRS model management
def get_prs_model_categories():
    """Get all available PRS model categories."""
    categories = set()
    for model in prs_models.values():
        if 'category' in model:
            categories.add(model['category'])
    return sorted(list(categories))

def get_prs_models_by_category(category):
    """Get all PRS models for a specific category."""
    return {name: model for name, model in prs_models.items()
            if model.get('category') == category}

def get_genomewide_models(trait_name):
    """Get genome-wide models for a specific trait."""
    if trait_name in prs_models and 'genomewide_models' in prs_models[trait_name]:
        return prs_models[trait_name]['genomewide_models']
    return []

def get_simple_model(trait_name):
    """Get simple model for a specific trait (for backward compatibility)."""
    if trait_name in prs_models and 'simple_model' in prs_models[trait_name]:
        return prs_models[trait_name]['simple_model']
    return None

def get_trait_description(trait_name):
    """Get description for a specific trait."""
    if trait_name in prs_models:
        return prs_models[trait_name].get('description', '')
    return ''

# Legacy support - maintain backward compatibility
def get_legacy_prs_models():
    """Get PRS models in the old simple format for backward compatibility."""
    legacy_models = {}
    for trait_name, model_data in prs_models.items():
        if 'simple_model' in model_data:
            legacy_models[trait_name] = model_data['simple_model']
    return legacy_models

guidance_data = {
    "Coronary Artery Disease": {
        "lifestyle": ["Maintain healthy weight (BMI 18.5-24.9)", "Regular aerobic exercise (150 min/week)", "Mediterranean diet", "No smoking", "Limit alcohol to 1 drink/day"],
        "monitoring": ["Regular blood pressure checks", "Cholesterol screening every 4-6 years", "HbA1c if diabetic"],
        "medical": ["Aspirin therapy if recommended", "Statin therapy if indicated", "ACE inhibitors for hypertension"],
        "screening": ["Regular cardiovascular risk assessment"]
    },
    "Type 2 Diabetes": {
        "lifestyle": ["Weight management", "150 min moderate exercise weekly", "Low glycemic index diet", "Portion control", "Stress management"],
        "monitoring": ["Annual HbA1c testing", "Regular blood glucose monitoring", "Kidney function tests", "Eye exams"],
        "medical": ["Metformin as first-line therapy", "Regular medication adherence", "Blood pressure control"],
        "screening": ["Annual diabetes screening if high risk"]
    },
    "Atrial Fibrillation": {
        "lifestyle": ["Weight management", "Regular exercise", "Limit caffeine and alcohol", "Stress reduction", "Sleep hygiene"],
        "monitoring": ["Regular heart rhythm monitoring", "Blood pressure checks", "Thyroid function tests"],
        "medical": ["Anticoagulation therapy if indicated", "Rate/rhythm control medications", "Regular cardiology follow-up"],
        "screening": ["Portable ECG monitoring if symptoms"]
    },
    "Ischemic Stroke": {
        "lifestyle": ["Blood pressure control", "Cholesterol management", "No smoking", "Regular exercise", "Healthy diet"],
        "monitoring": ["Regular blood pressure monitoring", "Cholesterol screening", "Carotid artery screening"],
        "medical": ["Antiplatelet therapy", "Statin therapy", "Antihypertensive medications"],
        "screening": ["Regular cardiovascular risk assessment"]
    },
    "Colorectal Cancer": {
        "lifestyle": ["High fiber diet", "Regular exercise", "Maintain healthy weight", "Limit red meat", "No smoking"],
        "monitoring": ["Regular colonoscopy", "FOBT/FIT testing", "Blood tests for anemia"],
        "medical": ["Chemoprevention if indicated", "Regular surveillance colonoscopy"],
        "screening": ["Colonoscopy every 1-3 years based on risk"]
    },
    "Prostate Cancer": {
        "lifestyle": ["Healthy diet", "Regular exercise", "Maintain healthy weight", "Limit calcium supplements"],
        "monitoring": ["Regular PSA testing", "Digital rectal exam", "Family history assessment"],
        "medical": ["Active surveillance if low-risk", "Regular urology follow-up"],
        "screening": ["PSA testing starting at age 50 (or earlier if high risk)"]
    },
    "Inflammatory Bowel Disease": {
        "lifestyle": ["Balanced nutrition", "Stress management", "Regular exercise", "Adequate sleep", "No smoking"],
        "monitoring": ["Regular colonoscopy", "Blood tests for inflammation", "Symptom tracking"],
        "medical": ["Immunomodulator therapy", "Regular gastroenterology follow-up", "Infection prevention"],
        "screening": ["Colonoscopy every 1-2 years"]
    },
    "Rheumatoid Arthritis": {
        "lifestyle": ["Regular exercise", "Joint protection techniques", "Healthy diet", "Weight management", "Stress reduction"],
        "monitoring": ["Regular joint assessments", "Blood tests for inflammation", "X-rays as needed"],
        "medical": ["DMARD therapy", "Regular rheumatology follow-up", "Pain management"],
        "screening": ["Early symptom recognition and reporting"]
    },
    "Systemic Lupus Erythematosus": {
        "lifestyle": ["Sun protection", "Healthy diet", "Regular exercise", "Stress management", "Adequate rest"],
        "monitoring": ["Regular blood tests", "Urine analysis", "Organ function monitoring"],
        "medical": ["Immunosuppressive therapy", "Regular specialist follow-up", "Infection prevention"],
        "screening": ["Regular comprehensive health assessments"]
    },
    "Multiple Sclerosis": {
        "lifestyle": ["Regular exercise", "Balanced diet", "Vitamin D supplementation", "Stress management", "Adequate sleep"],
        "monitoring": ["Regular neurological assessments", "MRI as indicated", "Symptom tracking"],
        "medical": ["Disease-modifying therapy", "Regular neurology follow-up", "Rehabilitation therapy"],
        "screening": ["Regular comprehensive evaluations"]
    },
    "Celiac Disease": {
        "lifestyle": ["Strict gluten-free diet", "Nutritional counseling", "Regular exercise", "Calcium/vitamin D intake"],
        "monitoring": ["Regular antibody testing", "Nutrient level monitoring", "Bone density scans"],
        "medical": ["Gluten-free diet adherence", "Regular gastroenterology follow-up"],
        "screening": ["Family member screening"]
    },
    "Major Depressive Disorder": {
        "lifestyle": ["Regular exercise", "Healthy diet", "Adequate sleep", "Social connections", "Stress management"],
        "monitoring": ["Regular mental health check-ins", "Symptom tracking", "Medication side effect monitoring"],
        "medical": ["Antidepressant therapy if indicated", "Regular therapy sessions", "Psychiatric follow-up"],
        "screening": ["Regular depression screening"]
    },
    "Schizophrenia": {
        "lifestyle": ["Medication adherence", "Regular routine", "Healthy diet", "Exercise", "Substance avoidance"],
        "monitoring": ["Regular psychiatric assessments", "Symptom monitoring", "Side effect tracking"],
        "medical": ["Antipsychotic therapy", "Regular psychiatric care", "Support services"],
        "screening": ["Regular mental health monitoring"]
    },
    "Osteoporosis": {
        "lifestyle": ["Weight-bearing exercise", "Calcium-rich diet", "Vitamin D intake", "No smoking", "Limit alcohol"],
        "monitoring": ["Bone density scans", "Calcium level monitoring", "Vitamin D level checks"],
        "medical": ["Bisphosphonate therapy if indicated", "Calcium/vitamin D supplements"],
        "screening": ["Bone density screening starting at age 65"]
    },
    "Asthma": {
        "lifestyle": ["Trigger avoidance", "Regular exercise", "Healthy diet", "Weight management", "Stress reduction"],
        "monitoring": ["Peak flow monitoring", "Regular pulmonary function tests", "Symptom tracking"],
        "medical": ["Inhaled corticosteroids", "Rescue inhaler use", "Regular allergy/pulmonary follow-up"],
        "screening": ["Regular asthma control assessments"]
    }
}