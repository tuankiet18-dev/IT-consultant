import { PageHead } from "../components/ui.jsx";
import { AuditTrail } from "./ApproveView.jsx";

export default function AuditView() {
  return (
    <div>
      <PageHead title="Audit trail" lead="Review data changes, planner decisions, approvals and exports." />
      <AuditTrail />
    </div>
  );
}
