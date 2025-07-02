
import csv, os

# Data path
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR     = os.path.join(BASE_DIR, "data")
HYG_CSV_PATH = os.path.join(DATA_DIR, "hygdata_v41.csv")

CONSTELLATION_NAMES = {
   "AND": "Andromeda", "ANT": "Antlia", "APS": "Apus", "AQL": "Aquila", "AQR": "Aquarius",
    "ARA": "Ara", "ARI": "Aries", "AUR": "Auriga", "BOO": "Boötes", "CAE": "Caelum",
    "CAM": "Camelopardalis", "CAP": "Capricornus", "CAR": "Carina", "CAS": "Cassiopeia",
    "CEN": "Centaurus", "CEP": "Cepheus", "CET": "Cetus", "CHA": "Chamaeleon", "CIR": "Circinus",
    "CMA": "Canis Major", "CMI": "Canis Minor", "CNC": "Cancer", "COL": "Columba", "COM": "Coma Berenices",
    "CRA": "Corona Australis", "CRB": "Corona Borealis", "CRT": "Crater", "CRU": "Crux", "CRV": "Corvus",
    "CVN": "Canes Venatici", "CYG": "Cygnus", "DEL": "Delphinus", "DOR": "Dorado", "DRA": "Draco",
    "EQU": "Equuleus", "ERI": "Eridanus", "FOR": "Fornax", "GEM": "Gemini", "GRU": "Grus",
    "HER": "Hercules", "HOR": "Horologium", "HYA": "Hydra", "HYI": "Hydrus", "IND": "Indus",
    "LAC": "Lacerta", "LEO": "Leo", "LEP": "Lepus", "LIB": "Libra", "LMI": "Leo Minor",
    "LUP": "Lupus", "LYN": "Lynx", "LYR": "Lyra", "MEN": "Mensa", "MIC": "Microscopium",
    "MON": "Monoceros", "MUS": "Musca", "NOR": "Norma", "OCT": "Octans", "OPH": "Ophiuchus",
    "ORI": "Orion", "PAV": "Pavo", "PEG": "Pegasus", "PER": "Perseus", "PHE": "Phoenix",
    "PIC": "Pictor", "PSA": "Piscis Austrinus", "PSC": "Pisces", "PUP": "Puppis", "PYX": "Pyxis",
    "RET": "Reticulum", "SCL": "Sculptor", "SCO": "Scorpius", "SCT": "Scutum", "SER": "Serpens",
    "SEX": "Sextans", "SGE": "Sagitta", "SGR": "Sagittarius", "TAH": "Taurus", "TEL": "Telescopium",
    "TRA": "Triangulum Australe", "TRI": "Triangulum", "TUC": "Tucana", "UMA": "Ursa Major",
    "UMI": "Ursa Minor", "VEL": "Vela", "VIR": "Virgo", "VOL": "Volans", "VUL": "Vulpecula"
}

def load_constellation_data():
    mapping = {}
    if not os.path.isfile(HYG_CSV_PATH):
        print(f"Warning: HYG data not found at {HYG_CSV_PATH}")
        return mapping

    with open(HYG_CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hip = int(float(row["hip"]))
                abbr = row["con"].upper()
                mapping[hip] = CONSTELLATION_NAMES.get(abbr, abbr)
            except Exception:
                continue
    return mapping
