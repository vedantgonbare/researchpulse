import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { PageShell } from "../components/PageShell";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Digest() {
  const { token } = useAuth();
  const [papers, setPapers] = useState([]);
  const [totalUnread, setTotalUnread] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [marking, setMarking] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function loadDigest() {
      setLoading(true);
      setError("");
      try {
        const data = await apiRequest("/papers/digest", { token });
        if (!cancelled) {
          setPapers(data.papers);
          setTotalUnread(data.total_unread);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadDigest();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const handleMarkAllRead = async () => {
    setMarking(true);
    try {
      await apiRequest("/papers/digest/mark-read", { method: "POST", token });
      // Optimistic: the backend finishes this in the background with no
      // "done" signal to poll for, so we clear the list immediately rather
      // than pretending to wait for a confirmation that doesn't exist.
      setPapers([]);
      setTotalUnread(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setMarking(false);
    }
  };

  return (
    <PageShell>
      <div className="flex flex-wrap gap-5 items-end justify-between">
        <div>
          <h1 className="text-[26px] font-extrabold text-brand-navy m-0">Digest</h1>
          <p className="mt-1.5 text-brand-text-muted text-sm">
            {totalUnread === 0 ? "You're all caught up!" : `${totalUnread} unread paper${totalUnread === 1 ? "" : "s"}`}
          </p>
        </div>
        {totalUnread > 0 && (
          <button
            type="button"
            onClick={handleMarkAllRead}
            disabled={marking}
            className="bg-brand-blue text-white text-sm font-bold px-5 py-2.5 rounded-full shadow-[0_6px_16px_rgba(79,110,247,0.3)] disabled:opacity-50"
          >
            {marking ? "Marking…" : "Mark all as read"}
          </button>
        )}
      </div>

      {loading && <p className="text-sm text-brand-text-muted">Loading digest…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {!loading && !error && papers.length === 0 && (
        <p className="text-sm text-brand-text-muted">No unread papers. You're all caught up!</p>
      )}

      {!loading && !error && papers.length > 0 && (
        <div className="grid gap-4" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(290px, 1fr))" }}>
          {papers.map((paper) => (
            <DigestCard key={paper.id} paper={paper} />
          ))}
        </div>
      )}
    </PageShell>
  );
}

function DigestCard({ paper }) {
  const tags = paper.tags ? paper.tags.split(",").map((t) => t.trim()).filter(Boolean) : [];

  return (
    <article className="bg-brand-surface rounded-[22px] p-5 flex flex-col gap-3 shadow-[0_2px_14px_rgba(27,37,89,0.05)]">
      <div className="flex items-start justify-between gap-2.5">
        <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-status-unread-bg text-status-unread-text">
          Unread
        </span>
        <span className="text-xs text-brand-text-faint font-semibold">{paper.saved_on}</span>
      </div>

      <h3 className="text-base font-bold leading-snug m-0">
        <Link to={`/papers/${paper.id}`}>{paper.title}</Link>
      </h3>
      <p className="text-[13px] text-brand-text-muted m-0">{paper.authors}</p>

      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-0.5">
          {tags.map((tag) => (
            <span key={tag} className="text-[11px] font-semibold bg-brand-field text-[#4F5A80] px-2.5 py-1 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      )}

      <Link to={`/papers/${paper.id}`} className="text-[13px] font-bold text-brand-blue mt-1 pt-3 border-t border-brand-field">
        {paper.ai_summary === "No summary yet — use /summarize endpoint" ? "Summarize" : "View summary"}
      </Link>
    </article>
  );
}