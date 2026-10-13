import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { Branch } from "../types";

// Список филиалов, доступных текущему пользователю.
export function useBranches(): Branch[] {
  const [branches, setBranches] = useState<Branch[]>([]);
  useEffect(() => {
    api.get<Branch[]>("/branches").then(setBranches).catch(() => setBranches([]));
  }, []);
  return branches;
}
