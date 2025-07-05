# constellation_utils.py
"""
Constellation utility functions for the Space Detective application.

This module provides functions to load constellation data and map HIP catalog 
IDs to their respective constellation names.
"""

import csv
import os

# --- Constants ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_CURRENT_DIR), 'data')
CONSTELLATION_FILE_PATH = os.path.join(_DATA_DIR, "hygdata_v41.csv")
HIP_COLUMN = 'hip'
CONSTELLATION_COLUMN = 'con'

# Mapping from constellation abbreviations to full names
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

# --- Public API/HYG data ---

def load_constellation_data(file_path=CONSTELLATION_FILE_PATH):
    """
    Load constellation data from the HYG star database CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary mapping a HIP ID (int) to a full constellation name (str).
    """
    constellation_map = {}
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    hip_str = row.get(HIP_COLUMN)
                    const_abbr = row.get(CONSTELLATION_COLUMN)

                    if hip_str and const_abbr:
                        hip_id = int(float(hip_str))
                        full_name = CONSTELLATION_NAMES.get(const_abbr.upper(), const_abbr)
                        constellation_map[hip_id] = full_name
                except (ValueError, TypeError):
                    # Skip rows with invalid data
                    continue
                    
    except (FileNotFoundError, Exception):
        # Return an empty map if the file is not found or another error occurs
        pass

    return constellation_map
