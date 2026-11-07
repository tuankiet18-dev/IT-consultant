import { useCallback, useRef, useState } from "react";
import AllocationFlow from "./AllocationFlow.jsx";
import RouteRanking from "./RouteRanking.jsx";

export default function AllocationExplorer({ run, ent }) {
  const [focusedPath, setFocusedPath] = useState(null);
  const diagram = useRef(null);
  const selectPath = useCallback(path => {
    setFocusedPath(path);
    if (path) requestAnimationFrame(() => diagram.current?.scrollIntoView({ behavior: "smooth", block: "center" }));
  }, []);
  const clearPath = useCallback(() => setFocusedPath(null), []);
  return (
    <div>
      <div ref={diagram}>
        <AllocationFlow plan={run.optimised} ent={ent} network={run.network} focusedPath={focusedPath} onClearPath={clearPath} />
      </div>
      {run.network && <RouteRanking run={run} ent={ent} focusedPath={focusedPath} onSelectPath={selectPath} />}
    </div>
  );
}
