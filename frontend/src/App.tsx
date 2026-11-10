import { useEffect, useState } from "react";
import { api, type AgentResponse, type Health, type Item, type ItemSummary, type Page } from "./api";
import "./App.css";

function ago(iso: string): string {
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 60) return `${mins} min ago`;
  if (mins < 1440) return `${Math.round(mins / 60)} h ago`;
  return `${Math.round(mins / 1440)} d ago`;
}

export default function App() {
  const [page, setPage] = useState<Page<Item> | null>(null);
  const [summary, setSummary] = useState<ItemSummary | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [priority, setPriority] = useState("");
  const [review, setReview] = useState<{ key: string; result?: AgentResponse; error?: string } | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
    // Counts come from the backend over all items, never from the rows on screen.
    api.summary().then(setSummary).catch(() => setSummary(null));
  }, []);

  useEffect(() => {
    setError(null);
    api.items(priority ? { priority } : {}).then(setPage).catch((e: Error) => setError(e.message));
  }, [priority]);

  function runReview(key: string) {
    setReview({ key });
    api.review(key).then((result) => setReview({ key, result })).catch((e: Error) => setReview({ key, error: e.message }));
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <h1>Example application</h1>
          <p className="sub">Replace this screen with your own. It shows the harness patterns end to end.</p>
        </div>
        <div className={`health ${health?.status ?? "down"}`}>
          {health
            ? `API ${health.status} · db ${health.database} · login ${health.auth_provider} · model ${health.llm_provider} · harness ${health.harness_version}`
            : "API unreachable"}
        </div>
      </header>

      <section className="kpis">
        <Kpi label="Items" value={summary?.total ?? "—"} />
        <Kpi label="Without owner" value={summary?.without_owner ?? "—"} warn={(summary?.without_owner ?? 0) > 0} />
        <Kpi label="Priority unknown" value={summary?.priority_unknown ?? "—"} warn={(summary?.priority_unknown ?? 0) > 0} />
      </section>
      <p className="asof">All items · data as of {summary?.data_as_of ? ago(summary.data_as_of) : "unknown"}</p>

      <section className="toolbar">
        <label>
          Priority
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option value="">All</option>
            {["high", "medium", "low", "unknown"].map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </label>
        {page && <span className="count">{page.items.length} of {page.total}</span>}
      </section>

      {error && <div className="error">Could not load items: {error}</div>}

      <table className="grid">
        <thead>
          <tr><th>Key</th><th>Title</th><th>Owner</th><th>Priority</th><th>Status</th><th>Updated</th><th>Gaps</th><th /></tr>
        </thead>
        <tbody>
          {(page?.items ?? []).map((item) => (
            <tr key={item.id}>
              <td className="mono">{item.item_key}</td>
              <td>{item.title}</td>
              <td>{item.owner ?? <span className="missing">missing</span>}</td>
              <td><span className={`pill pri-${item.priority}`}>{item.priority}</span></td>
              <td>{item.status}</td>
              <td>{ago(item.updated_at)}</td>
              <td className="small">{item.flags.join(", ") || "none"}</td>
              <td><button onClick={() => runReview(item.item_key)}>Review</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      {review && (
        <section className="review" aria-live="polite">
          <h2>Agent review of {review.key} <span className="advisory">advisory</span></h2>
          {!review.result && !review.error && <p className="sub">Running…</p>}
          {review.error && <div className="error">Review failed: {review.error}</div>}
          {review.result?.status === "failed" && <div className="error">Agent failed: {review.result.error}</div>}
          {review.result?.status === "succeeded" && (
            <>
              <p>{review.result.output.summary}</p>
              <p><strong>Suggested next step:</strong> {review.result.output.suggested_next_step}</p>
              <p className="small">
                Gaps (computed by rules): {review.result.output.flags?.join(", ") || "none"} · tool calls {review.result.tool_calls} ·
                model calls {review.result.llm_calls}
                {review.result.guardrail_events.length > 0 && ` · guardrails: ${review.result.guardrail_events.join(", ")}`}
              </p>
            </>
          )}
        </section>
      )}
    </main>
  );
}

function Kpi({ label, value, warn }: { label: string; value: number | string; warn?: boolean }) {
  return (
    <div className={`kpi ${warn ? "warn" : ""}`}>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}
