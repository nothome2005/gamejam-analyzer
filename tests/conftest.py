import sys
import os
import pytest
from datetime import datetime, timezone, timedelta

# Ensure src/ is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def sample_jam_dates():
    now = datetime.now(timezone.utc)
    return {
        "start_time": now + timedelta(days=1),
        "submission_deadline": now + timedelta(days=3),
        "review_deadline": now + timedelta(days=5)
    }

@pytest.fixture
def valid_sha256():
    return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
