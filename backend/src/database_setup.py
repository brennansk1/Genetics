import os
from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class SNPVariant(Base):
    __tablename__ = 'snps'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rsid = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    gene = Column(String)

class VariantInterpretation(Base):
    __tablename__ = 'variant_interpretations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rsid = Column(String, ForeignKey('snps.rsid'))
    genotype = Column(String) # e.g. "AA", "AG", "GG"
    interpretation = Column(Text)
    condition = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
    trait = Column(String, nullable=True)

class Guidance(Base):
    __tablename__ = 'guidance_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    condition = Column(String, unique=True, index=True)
    lifestyle = Column(JSON)
    monitoring = Column(JSON)
    medical = Column(JSON)
    screening = Column(JSON)

class AncestryPanel(Base):
    __tablename__ = 'ancestry_panels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    population = Column(String, index=True)
    rsid = Column(String)
    gene = Column(String)
    condition = Column(String)

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_FILE = os.path.join(_PROJECT_ROOT, 'data', 'genetics.db')
DB_PATH = f'sqlite:///{DB_FILE}'
engine = create_engine(DB_PATH)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    # Data to migrate from previous static dictionaries
    ancestry_panels_data = {
        "Ashkenazi Jewish": {
            "rs387906309": {"gene": "HEXA", "condition": "Tay-Sachs Disease"},
            "rs28940279": {"gene": "ASPA", "condition": "Canavan Disease"},
            "rs111033171": {"gene": "IKBKAP", "condition": "Familial Dysautonomia"},
            "rs113993962": {"gene": "BLM", "condition": "Bloom Syndrome"},
        },
        "Northern European": {
            "rs1800562": {"gene": "HFE", "condition": "Hereditary Hemochromatosis (C282Y)"},
            "rs1799945": {"gene": "HFE", "condition": "Hereditary Hemochromatosis (H63D)"},
        },
        "Mediterranean/South Asian": {
            "rs334": {"gene": "HBB", "condition": "Beta-thalassemia (p.Glu7Val)"},
            "rs33930165": {"gene": "HBB", "condition": "Beta-thalassemia (p.Glu7Lys)"},
            "rs33950507": {"gene": "HBB", "condition": "Beta-thalassemia (p.Glu27Lys)"},
        },
        "Southeast Asian": {
            "rs4149056": {"gene": "SLCO1B1", "condition": "Statin-induced myopathy risk"},
            "rs671": {"gene": "ALDH2", "condition": "Alcohol intolerance"},
        },
        "African Ancestry": {
            "rs334": {"gene": "HBB", "condition": "Sickle Cell Disease"},
            "rs113993960": {"gene": "CFTR", "condition": "Cystic Fibrosis (less common)"},
        },
    }
    
    guidance_data_static = {
        "Coronary Artery Disease": {
            "lifestyle": [
                "Adopt a Mediterranean diet rich in fruits, vegetables, and healthy fats",
                "Engage in at least 150 minutes of moderate aerobic activity per week",
                "Maintain a healthy weight (BMI 18.5-24.9)",
                "Quit smoking and limit alcohol intake",
            ],
            "monitoring": [
                "Regular blood pressure checks (at least annually)",
                "Lipid panel screening every 4-6 years (more frequent if high risk)",
                "Blood glucose monitoring if overweight or family history of diabetes",
            ],
            "medical": [
                "Discuss statin therapy with your doctor if LDL cholesterol is elevated",
                "Consider low-dose aspirin if recommended by a cardiologist",
                "Manage comorbidities like hypertension and diabetes aggressively",
            ],
            "screening": [
                "Coronary calcium scan (CAC) may be considered for risk refinement",
                "Stress testing if symptomatic",
            ],
        },
        "Type 2 Diabetes": {
            "lifestyle": [
                "Focus on a low-glycemic index diet with whole grains and fiber",
                "Aim for 5-7% weight loss if overweight",
                "Include resistance training 2-3 times per week",
                "Avoid sugary beverages and processed foods",
            ],
            "monitoring": [
                "Annual HbA1c testing",
                "Regular foot and eye exams if diagnosed",
                "Monitor blood pressure and cholesterol",
            ],
            "medical": [
                "Metformin may be considered for pre-diabetes",
                "Discuss GLP-1 agonists or SGLT2 inhibitors if high risk",
            ],
            "screening": [
                "Screening for diabetes starting at age 35 for overweight adults",
            ],
        },
        "Atrial Fibrillation": {
            "lifestyle": [
                "Limit alcohol consumption (a known trigger)",
                "Manage stress and treat sleep apnea if present",
                "Maintain a healthy weight to reduce burden on the heart",
            ],
            "monitoring": [
                "Monitor pulse for irregularity",
                "Use wearable devices (e.g., Apple Watch) for rhythm monitoring if advised",
            ],
            "medical": [
                "Anticoagulation therapy may be needed based on CHA2DS2-VASc score",
                "Rate or rhythm control medications as prescribed",
            ],
            "screening": [
                "Opportunistic screening for AFib in patients >65 years",
            ],
        },
        "Colorectal Cancer": {
            "lifestyle": [
                "Limit red and processed meat consumption",
                "Increase fiber intake from fruits, vegetables, and grains",
                "Maintain a healthy weight and stay active",
                "Limit alcohol and avoid tobacco",
            ],
            "monitoring": [
                "Monitor for symptoms like rectal bleeding or changes in bowel habits",
            ],
            "medical": [
                "Discuss aspirin chemoprevention with your doctor",
            ],
            "screening": [
                "Colonoscopy starting at age 45 (or earlier if high risk)",
                "Stool-based tests (FIT/Cologuard) as an alternative",
            ],
        },
    }

    db = SessionLocal()
    
    # Init Ancestry Panels
    if db.query(AncestryPanel).count() == 0:
        for pop, snps in ancestry_panels_data.items():
            for rsid, details in snps.items():
                panel_entry = AncestryPanel(
                    population=pop,
                    rsid=rsid,
                    gene=details['gene'],
                    condition=details['condition']
                )
                db.add(panel_entry)
        
    # Init Guidance Data
    if db.query(Guidance).count() == 0:
        for condition, g_data in guidance_data_static.items():
            g_entry = Guidance(
                condition=condition,
                lifestyle=g_data.get('lifestyle', []),
                monitoring=g_data.get('monitoring', []),
                medical=g_data.get('medical', []),
                screening=g_data.get('screening', [])
            )
            db.add(g_entry)
            
    db.commit()
    db.close()
    print("Database seeding completed.")

if __name__ == "__main__":
    init_db()
