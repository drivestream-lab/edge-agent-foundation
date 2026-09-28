"""Unit tests for domain models."""

from src.models import MilestoneType


def test_milestone_type_enum_values():
    assert MilestoneType.STAGED.value == "staged"
    assert MilestoneType.SHADOW_RUNNING.value == "shadow-running"
    assert MilestoneType.PROMOTED.value == "promoted"
    assert MilestoneType.REVERTED.value == "reverted"
    assert MilestoneType.FAILED.value == "failed"
    assert len(MilestoneType) == 5


def test_milestone_type_from_string():
    assert MilestoneType("promoted") == MilestoneType.PROMOTED
