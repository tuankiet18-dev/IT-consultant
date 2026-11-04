import { useApp } from "../store.jsx";
import { PageHead } from "../components/ui.jsx";
import { AuditTrail } from "./ApproveView.jsx";

export default function AuditView() {
  return (
    <div>
      <PageHead title="Audit trail" lead="A record of who did what, and when, for this scenario: data loaded, plans calculated, decisions, approvals and exports." />
      <AuditTrail />
    </div>
  );
}
