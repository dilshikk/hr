import { useEffect, useState, type FormEvent } from "react";
import { errorText, twofa } from "../api";
import { haptic } from "../telegram";

type Props = {
  mode: "setup" | "verify";
  challenge: string;
  onDone: () => void;
};

/** Второй шаг входа для Owner и HR Admin: первая настройка или ввод кода. */
export default function TwoFactor({ mode, challenge, onDone }: Props) {
  const [secret, setSecret] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [recovery, setRecovery] = useState<string[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (mode !== "setup") return;
    twofa.setup(challenge)
      .then((r) => setSecret(r.secret))
      .catch((e: unknown) => setError(errorText(e, "Не удалось начать настройку")));
  }, [mode, challenge]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "setup") {
        setRecovery(await twofa.confirm(challenge, code));
      } else {
        await twofa.verify(challenge, code);
        onDone();
      }
      haptic("success");
    } catch (err: unknown) {
      haptic("error");
      setError(errorText(err, "Не удалось проверить код"));
    } finally {
      setBusy(false);
    }
  }

  if (recovery) {
    return (
      <div className="app stack">
        <h1>Коды восстановления</h1>
        <p className="muted">
          Сохраните их в надёжном месте. Каждый код подходит один раз, если телефон с приложением потеряно. Снова они показаны не будут.
        </p>
        <ul className="list">
          {recovery.map((c) => (
            <li key={c} className="item static"><code>{c}</code></li>
          ))}
        </ul>
        <button className="btn" type="button" onClick={onDone}>Я сохранил(а) коды</button>
      </div>
    );
  }

  return (
    <form className="app stack" onSubmit={submit}>
      <h1>{mode === "setup" ? "Двухшаговая проверка" : "Код для входа"}</h1>

      {mode === "setup" ? (
        <>
          <p className="muted">
            Для вашей роли вход требует кода. Откройте приложение-аутентификатор (Google Authenticator, Authy и т.п.),
            добавьте аккаунт «вручную» с этим ключом и введите 6 цифр.
          </p>
          {secret ? <code className="item static">{secret}</code> : !error && <p className="muted">Готовим ключ…</p>}
        </>
      ) : (
        <p className="muted">Введите 6 цифр из приложения-аутентификатора или один из кодов восстановления.</p>
      )}

      <label>
        Код
        <input
          value={code}
          maxLength={32}
          autoComplete="one-time-code"
          inputMode={mode === "setup" ? "numeric" : "text"}
          placeholder={mode === "setup" ? "123 456" : "123 456 или a1b2c3d4-e5f6a7b8"}
          onChange={(e) => setCode(e.target.value)}
        />
      </label>

      {error && <p className="error">{error}</p>}

      <button className="btn" type="submit" disabled={busy || code.trim().length < 6 || (mode === "setup" && !secret)}>
        {busy ? "Проверка…" : "Подтвердить"}
      </button>
    </form>
  );
}
