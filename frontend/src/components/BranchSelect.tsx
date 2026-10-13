import type { Branch } from "../types";

type Props = { branches: Branch[]; value: string; onChange: (v: string) => void };

export default function BranchSelect({ branches, value, onChange }: Props) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Выберите филиал</option>
      {branches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
    </select>
  );
}
