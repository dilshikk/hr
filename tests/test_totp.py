import pyotp
import pytest

from app.core.totp import (
    TotpError,
    decrypt_secret,
    encrypt_secret,
    generate_recovery_codes,
    hash_recovery_code,
    is_totp_format,
    make_challenge,
    read_challenge,
    requires_2fa,
    verify_code,
)

SECRET = "JBSWY3DPEHPK3PXP"
NOW = 1_800_000_000
STEP = NOW // 30
KEY = "test-key"


def code_for(step: int) -> str:
    return pyotp.TOTP(SECRET, interval=30).generate_otp(step)


def test_correct_code_returns_its_time_step():
    assert verify_code(SECRET, code_for(STEP), now=NOW) == STEP


def test_wrong_code_is_rejected():
    wrong = "000000" if code_for(STEP) != "000000" else "111111"
    assert verify_code(SECRET, wrong, now=NOW) is None


def test_code_from_neighbour_step_is_accepted_for_clock_drift():
    assert verify_code(SECRET, code_for(STEP - 1), now=NOW) == STEP - 1


def test_expired_code_is_rejected():
    # Код двухминутной давности уже не подходит.
    assert verify_code(SECRET, code_for(STEP - 4), now=NOW) is None
    assert verify_code(SECRET, code_for(STEP + 4), now=NOW) is None


def test_code_with_spaces_is_accepted():
    code = code_for(STEP)
    assert verify_code(SECRET, f"{code[:3]} {code[3:]}", now=NOW) == STEP


@pytest.mark.parametrize("bad", ["", "12345", "1234567", "abcdef", "12-345"])
def test_malformed_code_is_rejected(bad):
    assert verify_code(SECRET, bad, now=NOW) is None


def test_totp_format_detection():
    assert is_totp_format("123 456")
    assert not is_totp_format("a1b2c3d4-e5f6a7b8")


def test_only_owner_and_hr_admin_need_2fa():
    assert requires_2fa("owner") and requires_2fa("hr_admin")
    assert not any(requires_2fa(r) for r in ("recruiter", "branch_manager", "viewer", "hacker"))


def test_secret_is_encrypted_and_roundtrips():
    encrypted = encrypt_secret(SECRET, KEY)
    assert SECRET not in encrypted
    assert decrypt_secret(encrypted, KEY) == SECRET


def test_secret_cannot_be_decrypted_with_other_key():
    with pytest.raises(TotpError):
        decrypt_secret(encrypt_secret(SECRET, KEY), "other-key")


def test_empty_encryption_key_is_refused():
    with pytest.raises(TotpError):
        encrypt_secret(SECRET, "")


def test_challenge_roundtrip():
    token = make_challenge(7, KEY, ttl_seconds=300, now=NOW)
    assert read_challenge(token, KEY, now=NOW + 10) == 7


def test_expired_challenge_is_rejected():
    token = make_challenge(7, KEY, ttl_seconds=300, now=NOW)
    with pytest.raises(TotpError):
        read_challenge(token, KEY, now=NOW + 301)


def test_tampered_challenge_is_rejected():
    # Подмена ID сотрудника при той же подписи не проходит.
    _, expires, signature = make_challenge(7, KEY, ttl_seconds=300, now=NOW).split(".")
    with pytest.raises(TotpError):
        read_challenge(f"1.{expires}.{signature}", KEY, now=NOW)


def test_challenge_with_other_key_is_rejected():
    token = make_challenge(7, KEY, ttl_seconds=300, now=NOW)
    with pytest.raises(TotpError):
        read_challenge(token, "other-key", now=NOW)


@pytest.mark.parametrize("bad", ["", "abc", "1.2", "x.2.3", "1.2.3.4"])
def test_malformed_challenge_is_rejected(bad):
    with pytest.raises(TotpError):
        read_challenge(bad, KEY, now=NOW)


def test_recovery_codes_are_unique_and_hash_ignores_format():
    codes = generate_recovery_codes()
    assert len(codes) == len(set(codes)) == 8
    code = codes[0]
    assert hash_recovery_code(code) == hash_recovery_code(code.upper().replace("-", " "))
    assert hash_recovery_code(code) != hash_recovery_code(codes[1])
