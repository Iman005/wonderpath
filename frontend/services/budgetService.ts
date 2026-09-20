import { apiClient } from "@/services/apiClient";
import type { Expense, TripBudget } from "@/shared/types";

export const budgetService = {
  getTripBudget: (tripId: string) => apiClient.get<TripBudget>(`/trips/${tripId}/budget`),
  addExpense: (tripId: string, payload: { label: string; amount: number }) =>
    apiClient.post<Expense>(`/trips/${tripId}/budget/expenses`, payload),
  removeExpense: (tripId: string, expenseId: string) =>
    apiClient.del<void>(`/trips/${tripId}/budget/expenses/${expenseId}`),
};
