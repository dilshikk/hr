export default function Placeholder({ title }: { title: string }) {
  return (
    <div className="card">
      <b>{title}</b>
      <p className="muted">Раздел появится в следующих версиях.</p>
    </div>
  );
}
