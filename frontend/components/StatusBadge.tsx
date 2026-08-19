interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config: Record<string, { cls: string; label: string }> = {
    Discovered: { cls: "badge-discovered", label: "Discovered" },
    Inferred: { cls: "badge-inferred", label: "Inferred" },
    "Pending Review": { cls: "badge-pending", label: "Pending Review" },
  };

  const { cls, label } = config[status] ?? { cls: "badge-pending", label: status };

  return (
    <span className={`badge ${cls}`} role="status" aria-label={`Status: ${label}`}>
      <span className="badge-dot" aria-hidden="true" />
      {label}
    </span>
  );
}
