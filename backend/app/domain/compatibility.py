"""Educational blood compatibility rules (requirements section 7, DT-1 and DT-2).

DISCLAIMER: ABO/Rh matching alone does not establish clinical suitability for
transfusion. This module explains a textbook rule; it never authorizes a transfusion.

Model
-----
Red cells: the donor's A/B antigens must all be present in the recipient (ABO rule),
and an Rh-positive donor cannot be matched to an Rh-negative recipient (Rh rule).
Plasma: reversed ABO logic, because plasma carries antibodies. Rh is ignored
(educational simplification stated in the report).
"""

from dataclasses import dataclass
from enum import StrEnum

VALID_GROUPS: tuple[str, ...] = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")


class Component(StrEnum):
    RED_CELLS = "RED_CELLS"
    PLASMA = "PLASMA"


class CompatibilityInputError(ValueError):
    """Invalid or missing input. `code` is machine-readable (DT-1 rules R1-R3)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class CompatibilityResult:
    compatible: bool
    rule_code: str
    explanation: str


def _antigens(group: str) -> frozenset[str]:
    """ABO antigens present on the cells, e.g. 'AB+' -> {'A','B'}, 'O-' -> {}."""
    return frozenset(group[:-1]) - {"O"}


def _is_rh_positive(group: str) -> bool:
    return group.endswith("+")


def _is_missing(value: object) -> bool:
    return value is None or value == ""


def _validate(donor: object, recipient: object, component: object) -> tuple[str, str, Component]:
    if _is_missing(donor) or _is_missing(recipient) or _is_missing(component):
        raise CompatibilityInputError(
            "MISSING_INPUT", "Donor group, recipient group and component are all required."
        )
    for label, value in (("donor", donor), ("recipient", recipient)):
        if value not in VALID_GROUPS:
            raise CompatibilityInputError(
                "INVALID_BLOOD_GROUP",
                f"Invalid {label} blood group. Expected one of {', '.join(VALID_GROUPS)}.",
            )
    try:
        parsed_component = Component(component)
    except ValueError:
        raise CompatibilityInputError(
            "UNSUPPORTED_COMPONENT",
            f"Unsupported component. Expected one of {', '.join(c.value for c in Component)}.",
        ) from None
    return str(donor), str(recipient), parsed_component


def check_compatibility(
    donor_group: object, recipient_group: object, component: object
) -> CompatibilityResult:
    """Return the educational compatibility result and the rule that produced it.

    Raises CompatibilityInputError for missing or invalid input.
    """
    donor, recipient, comp = _validate(donor_group, recipient_group, component)

    if comp is Component.RED_CELLS:
        if not _antigens(donor) <= _antigens(recipient):
            return CompatibilityResult(
                False, "ABO_MISMATCH", f"Donor {donor} has ABO antigens the recipient lacks."
            )
        if _is_rh_positive(donor) and not _is_rh_positive(recipient):
            return CompatibilityResult(
                False, "RH_MISMATCH", "Rh-positive red cells cannot go to an Rh-negative recipient."
            )
        return CompatibilityResult(
            True, "RULE_OK", f"Red cells from {donor} match {recipient} under the ABO/Rh rules."
        )

    # Plasma: recipient antigens must all be present on the donor (reversed ABO logic).
    if not _antigens(recipient) <= _antigens(donor):
        return CompatibilityResult(
            False,
            "PLASMA_ABO_MISMATCH",
            f"Plasma from {donor} carries antibodies against recipient {recipient}.",
        )
    return CompatibilityResult(
        True, "PLASMA_OK", f"Plasma from {donor} is ABO-compatible with {recipient}."
    )


def compatible_donor_groups(recipient_group: object, component: object) -> list[str]:
    """Advisory list of donor groups compatible with a recipient (never auto-allocated)."""
    if _is_missing(recipient_group) or _is_missing(component):
        raise CompatibilityInputError("MISSING_INPUT", "Recipient group and component required.")
    return [
        g for g in VALID_GROUPS if check_compatibility(g, recipient_group, component).compatible
    ]
