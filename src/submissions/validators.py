import re

class SubmissionValidationError(ValueError):
    """Raised when submission audit fields fail validation."""
    pass

SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")
GIT_URL_REGEX = re.compile(r"^(https?://|git@)[a-zA-Z0-9.-]+(/[a-zA-Z0-9_.-]+)+(\.git)?/?$")

def validate_sha256_hash(checksum: str) -> str:
    """
    Validates that checksum is exactly 64 hexadecimal characters (AC-F-003, BDD-SC-003).
    Normalizes to lower-case.
    """
    if not checksum or not isinstance(checksum, str):
        raise SubmissionValidationError("Контрольна сума повинна містити рівно 64 шістнадцяткові символи")

    cleaned = checksum.strip()
    if not SHA256_REGEX.match(cleaned):
        raise SubmissionValidationError("Контрольна сума повинна містити рівно 64 шістнадцяткові символи")

    return cleaned.lower()

def validate_git_url(url: str) -> str:
    """
    Validates git repository URL format.
    """
    if not url or not isinstance(url, str):
        raise SubmissionValidationError("Некоректний URL Git репозиторію")

    cleaned = url.strip()
    if not GIT_URL_REGEX.match(cleaned):
        raise SubmissionValidationError("Некоректний формат Git URL")

    return cleaned
