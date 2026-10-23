"""Decision-table tests for the compatibility module (requirements DT-1 and DT-2).

The expected matrices below are written out by hand from requirements sections 7.1
and 7.2 and are deliberately independent of the implementation, so the tests do not
simply re-run the code's own logic.
"""

import pytest

from app.domain.compatibility import (
    VALID_GROUPS,
    CompatibilityInputError,
    CompatibilityResult,
    Component,
    check_compatibility,
    compatible_donor_groups,
)

pytestmark = pytest.mark.unit

# Section 7.1: donor red cells -> recipients who can receive them
RED_CELL_MATRIX = {
    "O-": {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"},
    "O+": {"O+", "A+", "B+", "AB+"},
    "A-": {"A-", "A+", "AB-", "AB+"},
    "A+": {"A+", "AB+"},
    "B-": {"B-", "B+", "AB-", "AB+"},
    "B+": {"B+", "AB+"},
    "AB-": {"AB-", "AB+"},
    "AB+": {"AB+"},
}

# Section 7.2: recipient ABO type -> donor ABO types whose plasma is acceptable
PLASMA_MATRIX = {
    "O": {"O", "A", "B", "AB"},
    "A": {"A", "AB"},
    "B": {"B", "AB"},
    "AB": {"AB"},
}


def abo(group: str) -> str:
    return group[:-1]


# ---------- DT-1 rules R4-R7: red cell outcomes ----------


def test_dt1_r4_abo_and_rh_ok_is_compatible():
    result = check_compatibility("O+", "A+", Component.RED_CELLS)
    assert result == CompatibilityResult(True, "RULE_OK", result.explanation)


def test_dt1_r5_abo_ok_rh_fails_is_rh_mismatch():
    result = check_compatibility("A+", "AB-", "RED_CELLS")
    assert (result.compatible, result.rule_code) == (False, "RH_MISMATCH")


def test_dt1_r6_abo_fails_rh_ok_is_abo_mismatch():
    result = check_compatibility("A+", "B+", "RED_CELLS")
    assert (result.compatible, result.rule_code) == (False, "ABO_MISMATCH")


def test_dt1_r7_both_fail_reports_abo_mismatch_first():
    result = check_compatibility("A+", "O-", "RED_CELLS")
    assert (result.compatible, result.rule_code) == (False, "ABO_MISMATCH")


@pytest.mark.parametrize("donor", VALID_GROUPS)
@pytest.mark.parametrize("recipient", VALID_GROUPS)
def test_red_cells_all_64_pairs_match_reference_matrix(donor, recipient):
    result = check_compatibility(donor, recipient, Component.RED_CELLS)
    assert result.compatible == (recipient in RED_CELL_MATRIX[donor])
    assert result.rule_code in {"RULE_OK", "ABO_MISMATCH", "RH_MISMATCH"}
    assert (result.rule_code == "RULE_OK") == result.compatible


def test_o_negative_is_universal_red_cell_donor_and_ab_positive_universal_recipient():
    for recipient in VALID_GROUPS:
        assert check_compatibility("O-", recipient, "RED_CELLS").compatible
    for donor in VALID_GROUPS:
        assert check_compatibility(donor, "AB+", "RED_CELLS").compatible


# ---------- DT-2: plasma ----------


@pytest.mark.parametrize("donor", VALID_GROUPS)
@pytest.mark.parametrize("recipient", VALID_GROUPS)
def test_plasma_all_64_pairs_match_reference_matrix_ignoring_rh(donor, recipient):
    result = check_compatibility(donor, recipient, Component.PLASMA)
    assert result.compatible == (abo(donor) in PLASMA_MATRIX[abo(recipient)])
    assert result.rule_code == ("PLASMA_OK" if result.compatible else "PLASMA_ABO_MISMATCH")


def test_plasma_rh_is_ignored():
    assert check_compatibility("A+", "A-", "PLASMA").compatible
    assert check_compatibility("A-", "A+", "PLASMA").compatible


# ---------- DT-1 rules R1-R3: invalid input ----------


@pytest.mark.parametrize(
    ("donor", "recipient", "component"),
    [
        (None, "A+", "RED_CELLS"),
        ("A+", None, "RED_CELLS"),
        ("", "A+", "RED_CELLS"),
        ("A+", "", "RED_CELLS"),
        ("A+", "A+", None),
        ("A+", "A+", ""),
    ],
)
def test_dt1_r1_missing_input(donor, recipient, component):
    with pytest.raises(CompatibilityInputError) as exc:
        check_compatibility(donor, recipient, component)
    assert exc.value.code == "MISSING_INPUT"


@pytest.mark.parametrize(
    "bad_group", ["C+", "a+", "A+ ", " A+", "AB", "O", "A++", "+", "ab-", "0+", 5, ["A+"]]
)
def test_dt1_r2_invalid_group_in_either_position(bad_group):
    with pytest.raises(CompatibilityInputError) as donor_exc:
        check_compatibility(bad_group, "A+", "RED_CELLS")
    assert donor_exc.value.code == "INVALID_BLOOD_GROUP"
    with pytest.raises(CompatibilityInputError) as recipient_exc:
        check_compatibility("A+", bad_group, "RED_CELLS")
    assert recipient_exc.value.code == "INVALID_BLOOD_GROUP"


@pytest.mark.parametrize("bad_component", ["WHOLE_BLOOD", "red_cells", "PLATELETS", "RED CELLS", 7])
def test_dt1_r3_unsupported_component(bad_component):
    with pytest.raises(CompatibilityInputError) as exc:
        check_compatibility("A+", "A+", bad_component)
    assert exc.value.code == "UNSUPPORTED_COMPONENT"


def test_invalid_group_is_reported_before_unsupported_component():
    with pytest.raises(CompatibilityInputError) as exc:
        check_compatibility("Z+", "A+", "WHOLE_BLOOD")
    assert exc.value.code == "INVALID_BLOOD_GROUP"


def test_missing_input_is_reported_before_invalid_values():
    with pytest.raises(CompatibilityInputError) as exc:
        check_compatibility(None, "Z+", "WHOLE_BLOOD")
    assert exc.value.code == "MISSING_INPUT"


# ---------- Result explanation and advisory helper ----------


def test_every_result_carries_a_nonempty_explanation():
    for donor in VALID_GROUPS:
        for component in Component:
            assert check_compatibility(donor, "A+", component).explanation


def test_check_is_deterministic():
    first = check_compatibility("B-", "AB+", "RED_CELLS")
    assert all(check_compatibility("B-", "AB+", "RED_CELLS") == first for _ in range(5))


@pytest.mark.parametrize("recipient", VALID_GROUPS)
def test_compatible_donor_groups_red_cells_matches_matrix(recipient):
    expected = {d for d, allowed in RED_CELL_MATRIX.items() if recipient in allowed}
    assert set(compatible_donor_groups(recipient, "RED_CELLS")) == expected


def test_compatible_donor_groups_ab_positive_accepts_all_red_cells():
    assert compatible_donor_groups("AB+", "RED_CELLS") == list(VALID_GROUPS)


def test_compatible_donor_groups_o_negative_accepts_only_o_negative_red_cells():
    assert compatible_donor_groups("O-", "RED_CELLS") == ["O-"]


def test_compatible_donor_groups_requires_input():
    with pytest.raises(CompatibilityInputError):
        compatible_donor_groups(None, "RED_CELLS")
