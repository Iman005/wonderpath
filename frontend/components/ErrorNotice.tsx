import fa from "@/i18n/fa";

export default function ErrorNotice({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div
      className="card"
      style={{ borderColor: "var(--terracotta)", background: "var(--terracotta-tint)" }}
      role="alert"
    >
      <p style={{ margin: onRetry ? "0 0 12px" : 0, color: "var(--terracotta)", fontWeight: 700 }}>
        {message}
      </p>
      {onRetry && (
        <button className="btn btn-danger-outline btn-sm" onClick={onRetry}>
          {fa.common.retry}
        </button>
      )}
    </div>
  );
}
