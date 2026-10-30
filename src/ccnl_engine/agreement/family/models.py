"""Contract families: the central catalog and the family of one CCNL.

A contract family groups the CCNLs of one productive sector (for example
``metalmeccanica``) across employer size, legal form and signatories.  It is
descriptive metadata: no rule, rate or contribution regime is inherited from
it, and it is distinct from the INPS ``tax_sector``, from the CNEL code and
from the work groups G01-G17 of the completion roadmap, which the catalog
maps explicitly.  The Art. 12 TUIR dependants live in :mod:`ccnl_engine.family`,
an unrelated concept.
"""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["ContractFamily", "FamilyAssignment", "FamilyCatalog"]

#: Shape of a family id: lower-case words joined by hyphens.
FAMILY_ID = re.compile(r"[a-z]+(?:-[a-z]+)*")
#: Shape of a work group of the roadmap: ``G01`` to ``G17``.
WORK_GROUP = re.compile(r"G(0[1-9]|1[0-7])")


def _check_id(value: str) -> str:
    if not FAMILY_ID.fullmatch(value):
        msg = f"family id {value!r} is not lower-case words joined by hyphens"
        raise ValueError(msg)
    return value


class ContractFamily(BaseModel):
    """One family of the central catalog.

    Attributes:
        id: Stable identifier, the value of ``meta.family.id``; never
            reused for another family.
        name: Short English name.
        description: What the family covers.
        criteria: The test that assigns a CCNL to the family: the activity
            of the employer, not its INPS sector or its size.
        groups: Work groups G01-G17 of the roadmap that hold at least one
            CCNL of the family, recorded explicitly.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    criteria: str = Field(min_length=1)
    groups: tuple[str, ...] = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def _check_family_id(cls, value: str) -> str:
        return _check_id(value)

    @field_validator("groups")
    @classmethod
    def _check_groups(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        wrong = [group for group in value if not WORK_GROUP.fullmatch(group)]
        if wrong:
            msg = f"groups {wrong} are not work groups G01-G17"
            raise ValueError(msg)
        if list(value) != sorted(set(value)):
            msg = f"groups must be sorted and unique: {list(value)}"
            raise ValueError(msg)
        return value


class FamilyCatalog(BaseModel):
    """The central catalog of contract families.

    Attributes:
        schema_version: Version of the catalog format.
        families: The families, sorted by id.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int
    families: tuple[ContractFamily, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_ids(self) -> Self:
        ids = [family.id for family in self.families]
        if ids != sorted(set(ids)):
            msg = f"family ids must be sorted and unique: {ids}"
            raise ValueError(msg)
        return self

    @property
    def by_id(self) -> Mapping[str, ContractFamily]:
        """The families keyed by id."""
        return MappingProxyType({family.id: family for family in self.families})


class FamilyAssignment(BaseModel):
    """The family of one CCNL, ``meta.family``.

    Attributes:
        id: Id of the main family in the central catalog.
        reason: Why the CCNL belongs to the family: its scope as the text
            states it, and for a multi-sector text why this family prevails.
        related: Other families the text also touches (a craft agreement
            spanning two productions, a trade of agricultural produce),
            sorted; informative only.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    reason: str = Field(min_length=1)
    related: tuple[str, ...] = ()

    @field_validator("id")
    @classmethod
    def _check_family_id(cls, value: str) -> str:
        return _check_id(value)

    @model_validator(mode="after")
    def _check_related(self) -> Self:
        related = list(self.related)
        if related != sorted(set(related)) or self.id in related:
            msg = (
                f"family.related must be sorted, unique and exclude the main "
                f"family {self.id!r}: {related}"
            )
            raise ValueError(msg)
        return self

    @property
    def ids(self) -> tuple[str, ...]:
        """The main family followed by the related ones."""
        return (self.id, *self.related)
