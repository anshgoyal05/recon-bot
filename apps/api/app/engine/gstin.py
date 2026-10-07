import re
from typing import Tuple, Optional

# Standard 2-digit Indian State Codes under GST
GST_STATE_CODES = {
    "01": "Jammu and Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "26": "Dadra and Nagar Haveli and Daman and Diu",
    "27": "Maharashtra",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman and Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
}

GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

# Characters used for Modulo 36 checksum calculation
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHAR_MAP = {c: i for i, c in enumerate(CHARS)}

def compute_gstin_checksum(gstin_14: str) -> Optional[str]:
    """
    Computes the 15th character checksum for a 14-character GSTIN prefix
    using the official Modulo 36 algorithm.
    """
    if len(gstin_14) != 14:
        return None

    try:
        factor = 1
        total_sum = 0
        for char in gstin_14.upper():
            code_point = CHAR_MAP[char]
            digit = code_point * factor
            factor = 2 if factor == 1 else 1
            digit = (digit // 36) + (digit % 36)
            total_sum += digit

        remainder = total_sum % 36
        check_code_point = (36 - remainder) % 36
        return CHARS[check_code_point]
    except KeyError:
        return None

def validate_gstin(gstin: Optional[str]) -> Tuple[bool, str]:
    """
    Validates GSTIN format, state code, and Modulo 36 checksum.
    Returns (is_valid, error_message).
    """
    if not gstin or not isinstance(gstin, str):
        return False, "GSTIN is missing or empty."

    gstin_clean = gstin.strip().upper()
    if len(gstin_clean) != 15:
        return False, f"Invalid GSTIN length ({len(gstin_clean)} chars). Must be exactly 15 characters."

    if not GSTIN_REGEX.match(gstin_clean):
        return False, f"GSTIN '{gstin_clean}' does not match statutory alphanumeric pattern (2 digits + 5 chars + 4 digits + 1 char + 1 char + 'Z' + 1 checksum char)."

    state_code = gstin_clean[:2]
    if state_code not in GST_STATE_CODES:
        return False, f"Invalid State Code '{state_code}' in GSTIN '{gstin_clean}'."

    # Validate 15th check character
    expected_check_char = compute_gstin_checksum(gstin_clean[:14])
    actual_check_char = gstin_clean[14]

    # Note: Some testing GSTINs may have synthetic check characters, so check if mathematically matching
    if expected_check_char and expected_check_char != actual_check_char:
        # Checksum mismatch
        return False, f"GSTIN checksum failure: expected '{expected_check_char}', got '{actual_check_char}'."

    return True, "Valid GSTIN"

def get_state_code_from_gstin(gstin: Optional[str]) -> Optional[str]:
    if gstin and len(gstin.strip()) >= 2:
        return gstin.strip()[:2]
    return None

def get_state_name(state_code: Optional[str]) -> str:
    if state_code:
        return GST_STATE_CODES.get(state_code, f"State Code {state_code}")
    return "Unknown State"
