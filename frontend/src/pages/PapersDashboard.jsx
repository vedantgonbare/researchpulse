import { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import { PageShell } from "../components/PageShell";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function PapersDashboard() {
  const { token } = useAuth();
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all"); // "all" | "unread"

  useEffect(() => {
    let cancelled = false;

    async function loadPapers() {
      setLoading(true);
      setError("");
      try {
        const data = await apiRequest("/papers/", { token });
        if (!cancelled) setPapers(data);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadPapers();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const filteredPapers = useMemo(() => {
    return papers.filter((paper) => {
      if (filter === "unread" && paper.is_read) return false;
      if (!query.trim()) return true;
      const haystack = `${paper.title} ${paper.authors} ${paper.tags}`.toLowerCase();
      return haystack.includes(query.trim().toLowerCase());
    });
  }, [papers, query, filter]);

  const unreadCount = papers.filter((p) => !p.is_read).length;

  return (
    <PageShell>
      <TopBar />

      <div className="flex flex-wrap gap-5 items-end justify-between">
        <div>
          <h1 className="text-[26px] font-extrabold text-brand-navy m-0">My Library</h1>
          <p className="mt-1.5 text-brand-text-muted text-sm">
            {papers.length} papers saved · {unreadCount} unread
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div role="group" aria-label="Filter by read status" className="inline-flex bg-brand-surface rounded-full p-1 shadow-[0_2px_10px_rgba(27,37,89,0.05)]">
            <button
              type="button"
              onClick={() => setFilter("all")}
              className={`text-[13px] font-bold px-4 py-2 rounded-full ${
                filter === "all" ? "bg-brand-navy text-white" : "text-brand-text-muted"
              }`}
            >
              All
            </button>
            <button
              type="button"
              onClick={() => setFilter("unread")}
              className={`text-[13px] font-bold px-4 py-2 rounded-full ${
                filter === "unread" ? "bg-brand-navy text-white" : "text-brand-text-muted"
              }`}
            >
              Unread
            </button>
          </div>
          <Link
            to="/discover"
            className="inline-flex items-center gap-2 bg-brand-blue text-white text-sm font-bold px-5 py-2.5 rounded-full shadow-[0_6px_16px_rgba(79,110,247,0.3)]"
          >
            + Add from arXiv
          </Link>
        </div>
      </div>

      <SearchField value={query} onChange={setQuery} />

      {loading && <StateMessage text="Loading your library…" />}
      {error && <StateMessage text={error} isError />}
      {!loading && !error && filteredPapers.length === 0 && (
        <StateMessage text={papers.length === 0 ? "No papers saved yet." : "No papers match your search."} />
      )}

      {!loading && !error && filteredPapers.length > 0 && (
        <div className="grid gap-4" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(290px, 1fr))" }}>
          {filteredPapers.map((paper) => (
            <PaperCard key={paper.id} paper={paper} />
          ))}
        </div>
      )}
    </PageShell>
  );
}

function PaperCard({ paper }) {
  const tags = paper.tags ? paper.tags.split(",").map((t) => t.trim()).filter(Boolean) : [];
  const date = new Date(paper.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" });

  return (
    <article className="bg-brand-surface rounded-[22px] p-5 flex flex-col gap-3 shadow-[0_2px_14px_rgba(27,37,89,0.05)] transition-transform hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(27,37,89,0.08)]">
      <div className="flex items-start justify-between gap-2.5">
        <span
          className={`text-[11px] font-bold px-2.5 py-1 rounded-full ${
            paper.is_read
              ? "bg-status-read-bg text-status-read-text"
              : "bg-status-unread-bg text-status-unread-text"
          }`}
        >
          {paper.is_read ? "Read" : "Unread"}
        </span>
        <span className="text-xs text-brand-text-faint font-semibold">{date}</span>
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

      <div className="flex gap-4 mt-1 pt-3 border-t border-brand-field">
        <Link to={`/papers/${paper.id}`} className="text-[13px] font-bold text-brand-blue">
          {paper.ai_summary ? "Summarized" : "Summarize"}
        </Link>
        <Link to={`/papers/${paper.id}`} className="text-[13px] font-bold text-brand-text-faint">
          Notes
        </Link>
      </div>
    </article>
  );
}

function TopBar() {
  return (
    <div className="bg-brand-surface rounded-[20px] px-5 py-3.5 flex items-center gap-4 shadow-[0_2px_16px_rgba(27,37,89,0.05)]">
      <span className="text-sm font-semibold text-brand-text-muted">ResearchPulse</span>
    </div>
  );
}

function SearchField({ value, onChange }) {
  return (
    <div className="relative flex-1 max-w-[460px]">
      <label htmlFor="lib-search" className="sr-only">Search your library</label>
      <input
        id="lib-search"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search your saved papers…"
        className="w-full box-border px-4 py-2.5 rounded-full bg-brand-field text-sm text-brand-navy placeholder:text-brand-text-faint outline-none focus-visible:ring-2 focus-visible:ring-brand-blue"
      />
    </div>
  );
}

function StateMessage({ text, isError }) {
  return (
    <div className={`text-sm font-medium ${isError ? "text-red-600" : "text-brand-text-muted"}`}>
      {text}
    </div>
  );
}