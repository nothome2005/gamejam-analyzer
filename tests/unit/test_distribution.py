import pytest
from src.distribution.service import validate_build_distribution, DistributionError

def test_build_size_valid():
    assert validate_build_distribution("https://itch.io/game", 120.0) is True

def test_build_size_exceeds_500mb():
    with pytest.raises(DistributionError, match="перевищує допустимий ліміт джему"):
        validate_build_distribution("https://itch.io/game", 750.0)
