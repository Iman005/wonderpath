"use client";

import fa from "@/i18n/fa";

export default function BudgetWarning({
  message,
  onIncreaseCap,
  onReviewTrip,
}: {
  message: string;
  onIncreaseCap: () => void;
  onReviewTrip: () => void;
}) {
  return (
    <div
      className="card budget-warning"
      style={{ borderColor: "var(--terracotta)", background: "var(--terracotta-tint)", marginBottom: 20 }}
      role="status"
    >
      <p style={{ margin: "0 0 12px", color: "var(--terracotta)", fontWeight: 800 }}>
        {fa.budget.overBudgetWarning}
      </p>
      <p style={{ margin: "0 0 14px", color: "var(--terracotta)", fontWeight: 700 }}>{message}</p>
      <div className="row" style={{ flexWrap: "wrap" }}>
        <button className="btn btn-primary btn-sm" type="button" onClick={onIncreaseCap}>
          {fa.budget.increaseCap}
        </button>
        <button className="btn btn-outline btn-sm" type="button" onClick={onReviewTrip}>
          {fa.budget.reviewTripAndExpenses}
        </button>
      </div>
    </div>
  );
}
