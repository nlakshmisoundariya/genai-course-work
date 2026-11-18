"""Session 4: loan_rules.py — YOUR file

Picks up where Session 3 left off. clean_text.py cleaned and masked a raw
message; this module decides whether the applicant behind that message
qualifies for a loan. New tools this time: functions with default
arguments, a dataclass to hold the applicant's fields, type hints on every
signature, and two custom exceptions for two different kinds of "no".

Fill in each function body. Run the checkpoint with:
    uv run pytest tests/test_s04.py
"""

from dataclasses import dataclass


class InvalidApplicantError(Exception):
    """The applicant record itself is unusable (bad data, not a credit decision)."""


class LoanRejectedError(Exception):
    """The applicant record is fine, but does not qualify for the loan."""


MIN_CREDIT_SCORE = 650
MAX_FOIR = 0.5


@dataclass
class Applicant:
    name: str
    monthly_income: float
    existing_emi: float
    credit_score: int
    requested_emi: float


def validate_applicant(a: Applicant, min_credit_score: int = MIN_CREDIT_SCORE) -> None:
    """Raise InvalidApplicantError if the record itself cannot be used.

    This only checks that the numbers make sense (positive income, a score
    in range) — it is not yet asking whether the applicant qualifies.
    """
    if a.monthly_income <= 0:
        raise InvalidApplicantError("Monthly income must be positive.")
    if not 300 <= a.credit_score <= 900:
        raise InvalidApplicantError("Credit score must be between 300 and 900.")
    if a.existing_emi < 0:
        raise InvalidApplicantError("Existing EMI cannot be negative.")
    if a.requested_emi < 0:
        raise InvalidApplicantError("Requested EMI cannot be negative.")


def foir(a: Applicant) -> float:
    """Fixed Obligation to Income Ratio: total EMI load divided by income."""
    if a.monthly_income <= 0:
        raise InvalidApplicantError("Monthly income must be positive.")
    return (a.existing_emi + a.requested_emi) / a.monthly_income


def check_eligibility(
    a: Applicant,
    min_credit_score: int = MIN_CREDIT_SCORE,
    max_foir: float = MAX_FOIR,
) -> str:
    """Validate the record, then decide. Raises LoanRejectedError on a "no"."""
    validate_applicant(a, min_credit_score)
    if a.credit_score < min_credit_score:
        raise LoanRejectedError(
            f"credit score {a.credit_score} below {min_credit_score}"
        )
    ratio = foir(a)
    if ratio > max_foir:
        raise LoanRejectedError(
            f"FOIR {ratio:.2f} exceeds {max_foir:.2f}"
        )
    return f"{a.name}: approved, FOIR {ratio:.2f}"


def safe_check(a: Applicant) -> str:
    """Never raises. Turns any rejection or bad record into one friendly line."""
    try:
        return "Approved: " + check_eligibility(a, MIN_CREDIT_SCORE, MAX_FOIR)
    except LoanRejectedError as e:
        return f"Rejected: {a.name}: {e}"
    except InvalidApplicantError as e:
        return f"Invalid: {a.name}: {e}"


def summarise(applicants: list[Applicant]) -> dict[str, int]:
    """Count how many applicants in the list were approved, rejected, or invalid."""
    counts = {"approved": 0, "rejected": 0, "invalid": 0}
    for applicant in applicants:
        result = safe_check(applicant)
        if result.startswith("Approved:"):
            counts["approved"] += 1
        elif result.startswith("Rejected:"):
            counts["rejected"] += 1
        else:
            counts["invalid"] += 1
    return counts


APPLICANTS = [
    Applicant("Ravi", monthly_income=80000, existing_emi=10000, credit_score=720, requested_emi=15000),
    Applicant("Meera", monthly_income=40000, existing_emi=5000, credit_score=600, requested_emi=20000),
    Applicant("Zoya", monthly_income=0, existing_emi=0, credit_score=700, requested_emi=10000),
]

if __name__ == "__main__":
    for applicant in APPLICANTS:
        print(safe_check(applicant))
    print(summarise(APPLICANTS))
