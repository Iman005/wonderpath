export default function EmptyState({
  message,
  action,
}: {
  message: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="empty-state">
      <p style={{ margin: action ? "0 0 16px" : 0 }}>{message}</p>
      {action}
    </div>
  );
}
