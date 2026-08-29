"""
knowledge_base.py
------------------
Static domain knowledge used to turn a raw CV severity score into a
human-readable diagnosis + advice.
"""

CROPS = [
    "rice",
    "wheat",
    "maize",
    "tomato",
    "potato",
    "cotton",
    "sugarcane",
    "chili",
]

PARTS = ["leaf", "root"]

KNOWLEDGE_BASE = {
    "rice": {
        "leaf": {
            "disease": "Leaf Blast",
            "cause": "Fungus (Magnaporthe oryzae)",
            "management": [
                "Use resistant rice varieties where available",
                "Avoid excess nitrogen fertilizer",
                "Apply a tricyclazole-based fungicide at early symptoms",
                "Maintain proper field drainage",
            ],
        },
        "root": {
            "disease": "Bakanae / Root Rot",
            "cause": "Fungus (Fusarium fujikuroi / Fusarium spp.)",
            "management": [
                "Treat seeds with hot water (52-54C) before sowing",
                "Avoid water-logged, poorly drained soil",
                "Remove and destroy infected seedlings",
                "Use certified disease-free seed",
            ],
        },
    },
    "wheat": {
        "leaf": {
            "disease": "Leaf Rust",
            "cause": "Fungus (Puccinia triticina)",
            "management": [
                "Grow rust-resistant wheat varieties",
                "Apply propiconazole or tebuconazole fungicide",
                "Remove volunteer wheat plants that host the fungus",
                "Time sowing to avoid peak rust conditions",
            ],
        },
        "root": {
            "disease": "Take-all Root Rot",
            "cause": "Fungus (Gaeumannomyces graminis)",
            "management": [
                "Rotate with a non-cereal crop for 1-2 seasons",
                "Improve soil drainage",
                "Avoid continuous wheat monoculture",
                "Balance soil pH close to neutral",
            ],
        },
    },
    "maize": {
        "leaf": {
            "disease": "Northern Corn Leaf Blight",
            "cause": "Fungus (Exserohilum turcicum)",
            "management": [
                "Plant resistant hybrids",
                "Rotate crops and till crop residue under",
                "Apply a strobilurin-based fungicide if severe",
                "Avoid overhead irrigation late in the day",
            ],
        },
        "root": {
            "disease": "Stalk & Root Rot",
            "cause": "Fungus (Fusarium / Pythium spp.)",
            "management": [
                "Avoid drought or nutrient stress near maturity",
                "Maintain balanced potassium fertilization",
                "Improve field drainage",
                "Harvest promptly once mature to limit lodging",
            ],
        },
    },
    "tomato": {
        "leaf": {
            "disease": "Early Blight",
            "cause": "Fungus (Alternaria solani)",
            "management": [
                "Remove and destroy infected lower leaves",
                "Mulch to reduce soil splash onto foliage",
                "Apply copper-based or chlorothalonil fungicide",
                "Rotate with non-solanaceous crops",
            ],
        },
        "root": {
            "disease": "Fusarium Root Rot",
            "cause": "Fungus (Fusarium oxysporum)",
            "management": [
                "Use resistant tomato varieties (look for F/FF rating)",
                "Solarize soil before planting in infested fields",
                "Avoid over-watering / ensure good drainage",
                "Sterilize tools between plants",
            ],
        },
    },
    "potato": {
        "leaf": {
            "disease": "Late Blight",
            "cause": "Oomycete (Phytophthora infestans)",
            "management": [
                "Apply preventive fungicide (mancozeb / metalaxyl) in humid weather",
                "Destroy volunteer potato plants and cull piles",
                "Ensure good field ventilation / avoid dense canopies",
                "Use certified disease-free seed tubers",
            ],
        },
        "root": {
            "disease": "Black Scurf / Root Rot",
            "cause": "Fungus (Rhizoctonia solani)",
            "management": [
                "Use certified, disease-free seed tubers",
                "Rotate with cereals for 2-3 years",
                "Avoid planting into cold, wet soil",
                "Hill soil properly to reduce stem canker contact",
            ],
        },
    },
    "cotton": {
        "leaf": {
            "disease": "Bacterial Blight",
            "cause": "Bacterium (Xanthomonas citri pv. malvacearum)",
            "management": [
                "Use acid-delinted, treated seed",
                "Grow resistant cotton varieties",
                "Avoid overhead irrigation",
                "Remove and burn infected plant debris",
            ],
        },
        "root": {
            "disease": "Root Rot",
            "cause": "Fungus (Macrophomina phaseolina / Rhizoctonia spp.)",
            "management": [
                "Rotate with non-host crops like cereals",
                "Avoid water stress and maintain consistent irrigation",
                "Deep summer ploughing to expose fungal structures",
                "Apply Trichoderma-based bio-fungicide at sowing",
            ],
        },
    },
    "sugarcane": {
        "leaf": {
            "disease": "Red Rot (leaf/stalk phase)",
            "cause": "Fungus (Colletotrichum falcatum)",
            "management": [
                "Plant only disease-free, certified setts",
                "Hot water treat setts before planting",
                "Rotate with non-host crops",
                "Remove and burn severely infected clumps",
            ],
        },
        "root": {
            "disease": "Root Rot",
            "cause": "Fungus (Pythium / Fusarium spp.)",
            "management": [
                "Ensure well-drained fields, avoid waterlogging",
                "Use resistant varieties where available",
                "Treat setts with a fungicidal dip before planting",
                "Maintain balanced NPK fertilization",
            ],
        },
    },
    "chili": {
        "leaf": {
            "disease": "Cercospora Leaf Spot",
            "cause": "Fungus (Cercospora capsici)",
            "management": [
                "Avoid overhead irrigation, water at the base",
                "Apply copper oxychloride or mancozeb fungicide",
                "Remove and destroy fallen infected leaves",
                "Maintain adequate plant spacing for airflow",
            ],
        },
        "root": {
            "disease": "Damping-off / Root Rot",
            "cause": "Fungus (Pythium / Rhizoctonia spp.)",
            "management": [
                "Use well-drained, raised nursery beds",
                "Treat seeds with a bio-fungicide (Trichoderma) before sowing",
                "Avoid overwatering seedlings",
                "Disinfect nursery trays/soil before use",
            ],
        },
    },
}


def get_diagnosis(crop: str, part: str):
    """Return the disease profile dict for a crop/part, or None if unknown."""
    crop = crop.lower().strip()
    part = part.lower().strip()
    return KNOWLEDGE_BASE.get(crop, {}).get(part)
