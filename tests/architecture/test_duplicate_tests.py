"""No test is an exact duplicate of another; the inventory sees the suite.

The scan and the report per capability live in ``_test_inventory``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.architecture._test_inventory import collect, exact_duplicates, report

if TYPE_CHECKING:
    from pathlib import Path


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_suite_has_no_exact_duplicate() -> None:
    """Every test asserts something no other test asserts in the same way."""
    assert exact_duplicates(collect()) == []


def test_same_body_is_a_duplicate_whatever_the_docstring(tmp_path: Path) -> None:
    """Two tests differing only in name and docstring are duplicates."""
    body = "from m import f\n\n\ndef {name}():\n    '''{doc}'''\n    assert f() == 1\n"
    _write(tmp_path, "unit/test_a.py", body.format(name="test_a", doc="A."))
    _write(tmp_path, "unit/test_b.py", body.format(name="test_b", doc="B."))
    assert exact_duplicates(collect(tmp_path)) == [
        ("unit/test_a.py::test_a", "unit/test_b.py::test_b")
    ]


def test_same_body_on_other_imports_is_distinct(tmp_path: Path) -> None:
    """The same call to names imported from other modules is not a duplicate."""
    body = "from {module} import main\n\n\ndef test_x():\n    assert main() == 0\n"
    _write(tmp_path, "unit/test_a.py", body.format(module="a"))
    _write(tmp_path, "unit/test_b.py", body.format(module="b"))
    assert exact_duplicates(collect(tmp_path)) == []


def test_same_method_in_classes_of_other_fields_is_distinct(tmp_path: Path) -> None:
    """A method shared by classes holding different data is not a duplicate."""
    text = (
        "class TestA:\n    slug = 'a'\n\n    def test_x(self):\n"
        "        assert self.slug\n\n\n"
        "class TestB:\n    slug = 'b'\n\n    def test_x(self):\n"
        "        assert self.slug\n"
    )
    _write(tmp_path, "unit/test_c.py", text)
    assert exact_duplicates(collect(tmp_path)) == []


def test_report_counts_each_capability_per_level() -> None:
    """The report has a row per capability and lists multi-level modules."""
    text = report()
    assert "| payroll |" in text
    assert "| tax |" in text
    assert "Modules tested at more than one level:" in text


def test_report_maps_unit_and_acceptance_owners(tmp_path: Path) -> None:
    """A unit mirror and a public import of the same module share a frontier."""
    src = tmp_path / "src"
    _write(src, "payroll/event/inputs_variable_pay.py", "")
    _write(
        tmp_path,
        "tests/unit/ccnl_engine/payroll/event/test_inputs_variable_pay_more.py",
        "def test_x():\n    assert True\n",
    )
    _write(
        tmp_path,
        "tests/acceptance/public_api/test_events.py",
        "from ccnl_engine.events import BonusEvent\n\n\n"
        "def test_y():\n    assert BonusEvent\n",
    )
    text = report(tmp_path / "tests", src)
    assert "| payroll | 1 | 0 | 1 |" in text
    assert "- `payroll.event.inputs_variable_pay`: unit, acceptance" in text
