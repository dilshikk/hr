from backend.app.models import Candidate


def test_new_candidate_model_has_expected_fields():
    # Проверяем, что модель кандидата содержит поля, которые использует API.
    cols = set(Candidate.__table__.columns.keys())
    assert {"full_name", "phone", "branch_id", "vacancy_id", "stage"} <= cols


def test_candidate_stage_defaults_to_new():
    assert Candidate.__table__.columns["stage"].default.arg == "new"
