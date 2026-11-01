"""Defaults of the employer facts of a request."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, absence_is_fact, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["EMPLOYER_DEFAULTS"]

_REPORTED = FactEnforcement.REPORTED

#: Classification of the defaulted fields of the employer and its elements.
EMPLOYER_DEFAULTS: Mapping[str, FieldDefault] = {
    "EmployerProfile.activity": requires_fact(
        "notte_festivi_turni_substitute_tax",
        "employer.activity",
        _REPORTED,
        "unknown activity: the regime that excludes some activities is "
        "undetermined, with a blocker",
    ),
    "EmployerProfile.public_life_insurance": requires_fact(
        "inps_employee",
        "employer.public_life_insurance",
        _REPORTED,
        "the value the CCNL fixes; on a CCNL of the public administrations "
        "whose employers differ, the Assicurazione Sociale Vita is left out "
        "and the run has a missing_fact public_life_insurance blocker",
    ),
    "EmployerProfile.cigs_indotto": requires_fact(
        "inps_employer",
        "employer.cigs_indotto",
        FactEnforcement.REPORTED,
        "unknown indotto: a craft firm above fifteen employees is charged no "
        "CIGS, with an incomplete cigs_indotto_unknown issue",
    ),
    "EmployerProfile.fis_reduction": requires_fact(
        "inps_employee",
        "employer.fis_reduction",
        _REPORTED,
        "the full FIS rate; an employer of the fondo di integrazione salariale "
        "with up to five employees has a missing_fact fis_reduction blocker",
    ),
    "EmployerProfile.agricultural_zone": requires_fact(
        "inps_employer",
        "employer.agricultural_zone",
        _REPORTED,
        "the full employer rates; an agricultural run has a missing_fact "
        "agricultural_zone blocker",
    ),
    "EmployerProfile.provincial_pay_element": requires_fact(
        "base_salary",
        "employer.provincial_pay_element",
        _REPORTED,
        "the national element a provincial one replaces is left out; a level "
        "that pays one (Commercio terzo elemento) has a missing_fact "
        "provincial_pay_element blocker",
    ),
    "EmployerProfile.second_level_premium": requires_fact(
        "base_salary",
        "employer.second_level_premium",
        _REPORTED,
        "the element of guarantee a company premium replaces is left out; a "
        "level that pays one (Unionalimentari elemento di garanzia "
        "retributiva) has a missing_fact second_level_premium blocker",
    ),
    "EmployerProfile.inps_sector": requires_fact(
        "inps_employer",
        "employer.inps_sector",
        _REPORTED,
        "the INPS sector of the CCNL; a CCNL applied by employers of more "
        "than one sector (Logistica) has a missing_fact inps_sector blocker",
    ),
    "EmployerProfile.second_level_elements": absence_is_fact("none agreed"),
    "SecondLevelElement.valid_until": absence_is_fact("in force, no end"),
    "SecondLevelElement.levels": absence_is_fact("every level"),
    "SecondLevelElement.extra_months": absence_is_fact("paid on the extra months"),
    "SecondLevelElement.tfr_relevant": absence_is_fact("in the TFR base"),
    "EmployerProfile.contractual_funds": requires_fact(
        "contractual_funds",
        "employer.contractual_funds",
        _REPORTED,
        "unknown funds: on a CCNL that owes health or bilateral funds for "
        "every worker, their shares and the elemento distinto owed instead "
        "are left out and the run has a missing_fact contractual_funds "
        "blocker; an empty set states that the employer pays none",
    ),
}
