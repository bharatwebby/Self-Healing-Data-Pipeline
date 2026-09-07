import pytest
from pydantic import ValidationError

from schema.target import TargetRecord


def test_valid_record_is_accepted():
    record = TargetRecord(external_id=1, display_name="user_1", amount_cents=1500)
    assert record.external_id == 1
    assert record.amount_cents == 1500


def test_missing_field_is_rejected():
    with pytest.raises(ValidationError):
        TargetRecord(external_id=1, display_name="user_1")


def test_wrong_type_is_rejected():
    with pytest.raises(ValidationError):
        TargetRecord(external_id="not-an-int", display_name="user_1", amount_cents=100)


def test_extra_unexpected_field_does_not_silently_pass_through():
    # The whole point of the fixed schema is that source drift can add
    # extra junk fields (a new "meta" key, etc.) without corrupting the
    # target shape — pydantic drops unknown fields by default, which is
    # exactly the desired behavior here.
    record = TargetRecord(
        external_id=1, display_name="user_1", amount_cents=100, unexpected_field="junk"
    )
    assert not hasattr(record, "unexpected_field")
