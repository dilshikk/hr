type Props = { pct: number; color: string };

const R = 22;
const C = 2 * Math.PI * R;

export default function Ring({ pct, color }: Props) {
  return (
    <svg width="56" height="56" viewBox="0 0 56 56" aria-label={`${pct}%`}>
      <circle cx="28" cy="28" r={R} fill="none" stroke="#3a3a3a" strokeWidth="6" />
      <circle
        cx="28" cy="28" r={R} fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
        strokeDasharray={C} strokeDashoffset={C * (1 - pct / 100)} transform="rotate(-90 28 28)"
      />
      <text x="28" y="32" textAnchor="middle" fontSize="12" fill={color}>{pct}%</text>
    </svg>
  );
}
