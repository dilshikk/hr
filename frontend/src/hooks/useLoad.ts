import { useCallback, useEffect, useState } from "react";
import { errorText } from "../api";

/** Загрузка данных с состояниями «загрузка / ошибка / готово» и ручным обновлением. */
export function useLoad<T>(fn: () => Promise<T>, fallbackError: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setError(null);
    fn().then(setData).catch((e: unknown) => setError(errorText(e, fallbackError)));
    // fn и fallbackError задаются один раз на экран
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(reload, [reload]);
  return { data, error, reload, setData };
}
