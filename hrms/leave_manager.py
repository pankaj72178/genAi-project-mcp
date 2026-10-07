from collections import defaultdict
from typing import Dict

from hrms.schemas import LeaveApplyRequest


class LeaveManager:
    def __init__(self):
        self.employee_leaves: Dict[str, Dict] = defaultdict(
            lambda: {"balance": 20, "history": []}
        )

    def get_leave_balance(self, employee_id: str) -> str:
        data = self.employee_leaves.get(employee_id)
        if data:
            return f"{employee_id} has {data['balance']} leave days remaining."
        return "Employee ID not found."

    def _next_request_id(self) -> int:
        """
        Next request ID across all employees, so multi-day requests stay grouped.
        """
        ids = [
            record["request_id"]
            for data in self.employee_leaves.values()
            for record in data["history"]
        ]
        return max(ids, default=0) + 1

    def apply_leave(self, req: LeaveApplyRequest) -> str:
        employee_id = req.emp_id
        if employee_id not in self.employee_leaves:
            return "Employee ID not found."
        requested = len(req.leave_dates)
        available = self.employee_leaves[employee_id]["balance"]
        if available < requested:
            return f"Insufficient leave balance: requested {requested}, available {available}."
        self.employee_leaves[employee_id]["balance"] -= requested
        history = self.employee_leaves[employee_id]["history"]
        request_id = self._next_request_id()
        for leave_date in req.leave_dates:
            history.append({
                "history_id": len(history) + 1,
                "emp_id": employee_id,
                "leave_date": leave_date,
                "request_id": request_id,
            })
        return (f"Leave applied for {requested} day(s). Remaining balance: "
                f"{self.employee_leaves[employee_id]['balance']}")

    def get_leave_history(self, employee_id: str) -> str:
        data = self.employee_leaves.get(employee_id)
        if data is None:
            return "Employee ID not found."
        hist = data['history']
        if not hist:
            return f"{employee_id} has no leave history."
        dates = [record['leave_date'].strftime("%B %d, %Y") for record in hist]
        return f"Leave history for {employee_id}: {', '.join(dates)}."

if __name__ == "__main__":
    lm = LeaveManager()
    print(lm.get_leave_history("E004"))
