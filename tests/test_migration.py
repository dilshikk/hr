import importlib.util
import re
from pathlib import Path

from app.models import Base

MIGRATION = Path(__file__).resolve().parent.parent / "migrations" / "versions" / "0001_initial_schema.py"


def _source() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_migration_creates_every_model_table():
    # Если добавили модель, но забыли миграцию, тест упадёт.
    created = set(re.findall(r'op\.create_table\(\s*"(\w+)"', _source()))
    assert created == set(Base.metadata.tables.keys())


def test_migration_columns_match_models():
    source = _source()
    for name, table in Base.metadata.tables.items():
        block = source.split(f'"{name}",', 1)[1].split("op.create_table", 1)[0]
        for column in table.columns.keys():
            assert f'"{column}"' in block, f"{name}.{column} отсутствует в миграции"


def test_downgrade_drops_every_table():
    downgrade = _source().split("def downgrade", 1)[1]
    dropped = set(re.findall(r'"(\w+)"', downgrade))
    assert set(Base.metadata.tables.keys()) <= dropped


def test_migration_is_loadable_and_is_first_revision():
    spec = importlib.util.spec_from_file_location("migration_0001", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.revision == "0001"
    assert module.down_revision is None
