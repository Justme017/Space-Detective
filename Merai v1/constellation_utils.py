# constellation_utils.py
import csv

# Updated file path to the new CSV data source
CONSTELLATION_FILE_PATH = r"D:\\NITM ED\\Coding - Python\\GITHUB\\Space-Detective\\Merai v1\\hygdata_v41.csv"

# Full constellation names from abbreviations (remains the same)
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

def load_constellation_data(file_path=CONSTELLATION_FILE_PATH):
    """Loads constellation data from the hygdata_v41.csv file.
    Assumes CSV format with a header. Looks for 'hip' and 'con' columns.
    Returns a dictionary mapping HIP ID (int) to full constellation name (str).
    """
    constellation_map = {}
    hip_col_index = -1
    con_col_index = -1

    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Read the header row
            
            # Find column indices for 'hip' and 'con'
            try:
                hip_col_index = header.index('hip')
                con_col_index = header.index('con')
            except ValueError:
                print("Error: 'hip' or 'con' column not found in CSV header.")
                print(f"Header found: {header}")
                return constellation_map # Return empty map if columns are not found

            for row in reader:
                try:
                    # Ensure row has enough columns
                    if len(row) > max(hip_col_index, con_col_index):
                        hip_str = row[hip_col_index]
                        const_abbr = row[con_col_index].upper()

                        if hip_str and const_abbr: # Ensure values are not empty
                            hip_id = int(float(hip_str)) # HIP ID might be float in some CSVs, convert to int
                            constellation_map[hip_id] = CONSTELLATION_NAMES.get(const_abbr, const_abbr)
                    else:
                        # Log or handle rows that are too short, if necessary
                        # print(f"Skipping short row: {row}")
                        continue
                except ValueError:
                    # Skip lines that don't conform to expected HIP ID (numeric) or other parsing errors
                    # print(f"Skipping row due to ValueError: {row}")
                    continue
                except IndexError:
                    # Should be caught by len(row) check, but as a safeguard
                    # print(f"Skipping row due to IndexError: {row}")
                    continue
    except FileNotFoundError:
        print(f"Error: Constellation file not found at {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
        
    # A quick check for Taurus abbreviation, as 'TAH' was noted and 'TAU' is common
    if "TAH" in CONSTELLATION_NAMES and "TAU" not in CONSTELLATION_NAMES:
        print("Note: 'TAH' is used for Taurus. If 'TAU' is expected from CSV, update CONSTELLATION_NAMES.")

    return constellation_map
