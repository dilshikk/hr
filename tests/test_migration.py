import importlib.util
import re
from pathlib import Path

from app.models import Base

VERSIONS = Path(__file__).resolve().parent.parent / "migrations" / "versions"


def _files() -> list[Path]:
    return sorted(VERSIONS.glob("0*.py"))


def _sources() -> list[str]:
    return [p.read_text(encoding="utf-8") for p in _files()]


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"migration_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migrations_create_every_model_table():
    # Если добавили модель, но забыли миграцию, тест упадёт.
    created: set[str] = set()
    for source in _sources():
        created |= set(re.findall(r'op\.create_table\(\s*"(\w+)"', source))
    assert created == set(Base.metadata.tables.keys())


def test_migration_columns_match_models():
    sources = _sources()
    all_source = "\n".join(sources)
    for name, table in Base.metadata.tables.items():
        source = next(s for s in sources if re.search(rf'op\.create_table\(\s*"{name}"', s))
        block = source.split(f'"{name}",', 1)[1].split("op.create_table", 1)[0]
        # Колонки, добавленные позже отдельной командой add_column, тоже считаются.
        added = set(re.findall(rf'op\.add_column\(\s*"{name}",\s*sa\.Column\(\s*"(\w+)"', all_source))
        for column in table.columns.keys():
            assert f'"{column}"' in block or column in added, f"{name}.{column} отсутствует в миграции"


def test_downgrades_drop_every_table():
    dropped: set[str] = set()
    for source in _sources():
        dropped |= set(re.findall(r'"(\w+)"', source.split("def downgrade", 1)[1]))
    assert set(Base.metadata.tables.keys()) <= dropped


def test_downgrade_removes_added_columns():
    source = (VERSIONS / "0004_reminders_documents_links.py").read_text(encoding="utf-8")
    added = re.findall(r'op\.add_column\(\s*"(\w+)",\s*sa\.Column\(\s*"(\w+)"', source)
    assert added
    down = source.split("def downgrade", 1)[1]
    for table, column in added:
        assert f'op.drop_column("{table}", "{column}")' in down


def test_migrations_form_a_single_chain():
    modules = [_load(p) for p in _files()]
    assert modules[0].revision == "0001"
    assert modules[0].down_revision is None
    for previous, current in zip(modules, modules[1:]):
        assert current.down_revision == previous.revision
