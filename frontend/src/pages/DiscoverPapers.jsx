import { useState, useEffect } from "react";
import { PageShell } from "../components/PageShell";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function DiscoverPapers() {
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [resultSource, setResultSource] = useState(null); // "cache" | "arxiv"
  const [savedIds, setSavedIds] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [savingId, setSavingId] = useState(null); // which arxiv_id is mid-save
  const [saveErrors, setSaveErrors] = useState({}); // arxiv_id -> message

  // Load the user's existing library once, so we know what's already saved
  useEffect(() => {
    let cancelled = false;
    async function loadLibrary() {
      try {
        const data = await apiRequest("/papers/", { token });
        if (!cancelled) {
          setSavedIds(new Set(data.map((p) => p.arxiv_id)));
        }
      } catch {
        // non-fatal: worst case, "Save" stays clickable and the backend's
        // own duplicate-check catches it instead
      }
    }
    loadLibrary();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearchError("");
    try {
      const data = await apiRequest(
        `/papers/search?q=${encodeURIComponent(query.trim())}&max_results=10`,
        { token }
      );
      setResults(data.results);
      setResultSource(data.source);
    } catch (err) {
      setSearchError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (arxivId) => {
    setSavingId(arxivId);
    setSaveErrors((prev) => ({ ...prev, [arxivId]: "" }));
    try {
      await apiRequest("/papers/", {
        method: "POST",
        token,
        body: { arxiv_id: arxivId },
      });
      setSavedIds((prev) => new Set(prev).add(arxivId));
    } catch (err) {
      setSaveErrors((prev) => ({ ...prev, [arxivId]: err.message }));
    } finally {
      setSavingId(null);
    }
  };

  return (
    <PageShell>
      <div>
        <h1 className="text-[26px] font-extrabold text-brand-navy m-0">Discover Papers</h1>
        <p className="mt-1.5 text-brand-text-muted text-sm">
          Search arXiv and save papers to your library
        </p>
      </div>

      <form
        onSubmit={handleSearch}
        className="bg-brand-surface rounded-[20px] p-2.5 flex gap-2.5 shadow-[0_2px_16px_rgba(27,37,89,0.05)]"
      >
        <label htmlFor="discover-search" className="sr-only">
          Search arXiv
        </label>
        <input
          id="discover-search"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search arXiv by keyword…"
          className="flex-1 box-border px-4 py-3 rounded-2xl bg-brand-field text-sm text-brand-navy placeholder:text-brand-text-faint outline-none focus-visible:ring-2 focus-visible:ring-brand-blue"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-brand-blue text-white text-sm font-bold px-6 rounded-2xl disabled:opacity-50"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {searchError && <p className="text-sm text-red-600">{searchError}</p>}

      {resultSource && (
        <p className="text-[13px] text-brand-text-faint font-semibold">
          {results.length} results · {resultSource === "cache" ? "cached" : "fresh from arXiv"}
        </p>
      )}

      <div className="flex flex-col gap-3.5">
        {results.map((paper) => {
          const isSaved = savedIds.has(paper.arxiv_id);
          const isSaving = savingId === paper.arxiv_id;
          const saveError = saveErrors[paper.arxiv_id];

          return (
            <article
              key={paper.arxiv_id}
              className="bg-brand-surface rounded-[20px] px-5.5 py-5 flex items-start gap-4.5 shadow-[0_2px_14px_rgba(27,37,89,0.05)]"
            >
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-bold leading-snug m-0 mb-1.5">{paper.title}</h3>
                <p className="text-[13px] text-brand-text-muted m-0 mb-2.5">{paper.authors}</p>
                <p className="text-[13px] text-brand-text-muted leading-relaxed m-0 line-clamp-2">
                  {paper.abstract}
                </p>
                {saveError && <p className="text-xs text-red-600 mt-1.5">{saveError}</p>}
              </div>

              {isSaved ? (
                <span className="flex-none inline-flex items-center gap-1.5 bg-status-read-bg text-status-read-text text-[13px] font-bold px-4.5 py-2.5 rounded-full">
                  ✓ Saved
                </span>
              ) : (
                <button
                  type="button"
                  onClick={() => handleSave(paper.arxiv_id)}
                  disabled={isSaving}
                  className="flex-none inline-flex items-center gap-1.5 bg-brand-field text-brand-blue text-[13px] font-bold px-4.5 py-2.5 rounded-full disabled:opacity-50"
                >
                  {isSaving ? "Saving…" : "+ Save"}
                </button>
              )}
            </article>
          );
        })}
      </div>

      {!loading && results.length === 0 && !searchError && (
        <p className="text-sm text-brand-text-muted">Search arXiv above to find papers to save.</p>
      )}
    </PageShell>
  );
}