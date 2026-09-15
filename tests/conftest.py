from pathlib import Path
import pytest


FIXTURES = Path(__file__).parents[1] / "fixtures"


@pytest.fixture
def fixture_text():
    return lambda name: (FIXTURES / name).read_text(encoding="utf-8")

