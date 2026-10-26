import pytest
from src.submissions.validators import validate_sha256_hash, SubmissionValidationError

def test_validate_sha256_valid_lowercase():
    h = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert validate_sha256_hash(h) == h

def test_validate_sha256_valid_uppercase_normalized():
    h_upper = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
    assert validate_sha256_hash(h_upper) == h_upper.lower()

def test_validate_sha256_invalid_too_short():
    with pytest.raises(SubmissionValidationError, match="Контрольна сума повинна містити рівно 64 шістнадцяткові символи"):
        validate_sha256_hash("too-short-hash")

def test_validate_sha256_invalid_non_hex_chars():
    bad_chars = "z" * 64
    with pytest.raises(SubmissionValidationError):
        validate_sha256_hash(bad_chars)
