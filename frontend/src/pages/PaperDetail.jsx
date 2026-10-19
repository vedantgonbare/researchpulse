import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { PageShell } from "../components/PageShell";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function PaperDetail() {
  const { id } = useParams();
  const { token } = useAuth();

  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [notesDraft, setNotesDraft] = useState("");
  const [tagInput, setTagInput] = useState("");
  const [savingTags, setSavingTags] = useState(false);
  const [savingRead, setSavingRead] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [summarizeError, setSummarizeError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadPaper() {
      setLoading(true);
      setError("");
      try {
        const data = await apiRequest(`/papers/${id}`, { token });
        if (!cancelled) {
          setPaper(data);
          setNotesDraft(data.notes || "");
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadPaper();
    return () => {
      cancelled = true;
    };
  }, [id, token]);

  const patchPaper = useCallback(
    async (partial) => {
      const updated = await apiRequest(`/papers/${id}`, {
        method: "PATCH",
        token,
        body: partial,
      });
      setPaper(updated);
      return updated;
    },
    [id, token]
  );

  const handleNotesBlur = async () => {
    if (notesDraft === (paper.notes || "")) return; // nothing changed, skip the call
    try {
      await patchPaper({ notes: notesDraft });
    } catch (err) {
      setError(`Couldn't save notes: ${err.message}`);
    }
  };

  const handleAddTag = async (e) => {
    if (e.key !== "Enter" || !tagInput.trim()) return;
    e.preventDefault();
    const existing = paper.tags ? paper.tags.split(",").map((t) => t.trim()).filter(Boolean) : [];
    if (existing.includes(tagInput.trim())) {
      setTagInput("");
      return;
    }
    const nextTags = [...existing, tagInput.trim()].join(",");
    setTagInput("");
    setSavingTags(true);
    try {
      await patchPaper({ tags: nextTags });
    } catch (err) {
      setError(`Couldn't add tag: ${err.message}`);
    } finally {
      setSavingTags(false);
    }
  };

  const handleRemoveTag = async (tagToRemove) => {
    const existing = paper.tags.split(",").map((t) => t.trim()).filter(Boolean);
    const nextTags = existing.filter((t) => t !== tagToRemove).join(",");
    setSavingTags(true);
    try {
      await patchPaper({ tags: nextTags });
    } catch (err) {
      setError(`Couldn't remove tag: ${err.message}`);
    } finally {
      setSavingTags(false);
    }
  };

  const handleToggleRead = async () => {
    setSavingRead(true);
    try {
      await patchPaper({ is_read: !paper.is_read });
    } catch (err) {
      setError(`Couldn't update read status: ${err.message}`);
    } finally {
      setSavingRead(false);
    }
  };

  const handleSummarize = async () => {
    setSummarizing(true);
    setSummarizeError("");
    try {
      const updated = await apiRequest(`/papers/${id}/summarize`, {
        method: "POST",
        token,
      });
      setPaper(updated);
    } catch (err) {
      setSummarizeError(err.message);
    } finally {
      setSummarizing(false);
    }
  };

  if (loading) {
    return (
      <PageShell>
        <p className="text-sm text-brand-text-muted">Loading paper…</p>
      </PageShell>
    );
  }

  if (error && !paper) {
    return (
      <PageShell>
        <p className="text-sm text-red-600">{error}</p>
        <Link to="/dashboard" className="text-sm font-bold text-brand-blue">
          Back to My Library
        </Link>
      </PageShell>
    );
  }

  const tags = paper.tags ? paper.tags.split(",").map((t) => t.trim()).filter(Boolean) : [];
  const savedDate = new Date(paper.created_at).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });

  return (
    <PageShell>
      <Link
        to="/dashboard"
        className="inline-flex items-center gap-1.5 text-[13px] font-bold text-brand-text-muted w-fit"
      >
        ← Back to My Library
      </Link>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex flex-wrap gap-6 items-start">
        {/* Main paper info */}
        <div className="flex-1 min-w-[420px] bg-brand-surface rounded-[22px] p-7 shadow-[0_2px_16px_rgba(27,37,89,0.05)] flex flex-col gap-4">
          <div className="flex items-center gap-2.5">
            <span
              className={`text-[11px] font-bold px-2.5 py-1 rounded-full ${
                paper.is_read
                  ? "bg-status-read-bg text-status-read-text"
                  : "bg-status-unread-bg text-status-unread-text"
              }`}
            >
              {paper.is_read ? "Read" : "Unread"}
            </span>
            <span className="text-xs text-brand-text-faint font-semibold">
              Saved {savedDate} · arXiv {paper.arxiv_id}
            </span>
          </div>

          <h1 className="text-[22px] font-extrabold leading-snug m-0">{paper.title}</h1>
          <p className="text-sm text-brand-text-muted m-0">{paper.authors}</p>
          <p className="text-sm leading-relaxed text-[#363E63] m-0">{paper.abstract}</p>

          <div className="flex flex-wrap gap-2.5 mt-1">
            <a
              href={paper.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 border border-brand-border text-brand-navy text-[13px] font-bold px-4 py-2 rounded-full"
            >
              View on arXiv
            </a>
            <button
              type="button"
              onClick={handleToggleRead}
              disabled={savingRead}
              className="inline-flex items-center gap-2 bg-brand-field text-brand-blue text-[13px] font-bold px-4 py-2 rounded-full disabled:opacity-50"
            >
              {savingRead ? "Saving…" : paper.is_read ? "Mark as unread" : "Mark as read"}
            </button>
          </div>
        </div>

        {/* Side panel */}
        <div className="flex-1 min-w-[280px] flex flex-col gap-4.5">
          {/* AI Summary */}
          <div className="bg-brand-surface rounded-[22px] p-5.5 shadow-[0_2px_16px_rgba(27,37,89,0.05)] flex flex-col gap-3.5">
            <h2 className="text-[15px] font-extrabold m-0">AI Summary</h2>
            {paper.ai_summary ? (
              <p className="text-[13px] leading-relaxed text-[#363E63] m-0">{paper.ai_summary}</p>
            ) : (
              <>
                <button
                  type="button"
                  onClick={handleSummarize}
                  disabled={summarizing}
                  className="bg-brand-blue text-white text-[13px] font-bold py-2.5 rounded-2xl shadow-[0_6px_16px_rgba(79,110,247,0.25)] disabled:opacity-50"
                >
                  {summarizing ? "Generating…" : "Summarize abstract"}
                </button>
                {summarizeError ? (
                  <p className="text-xs text-red-600">{summarizeError}</p>
                ) : (
                  <p className="text-xs text-brand-text-faint">No summary yet — generate one with Gemini.</p>
                )}
              </>
            )}
          </div>

          {/* Tags */}
          <div className="bg-brand-surface rounded-[22px] p-5.5 shadow-[0_2px_16px_rgba(27,37,89,0.05)] flex flex-col gap-2.5">
            <h2 className="text-[15px] font-extrabold m-0">Tags</h2>
            <div className="flex flex-wrap gap-1.5">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[11px] font-semibold bg-brand-field text-[#4F5A80] px-3 py-1.5 rounded-full inline-flex items-center gap-1.5"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    disabled={savingTags}
                    aria-label={`Remove tag ${tag}`}
                    className="opacity-50 hover:opacity-100"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleAddTag}
              disabled={savingTags}
              placeholder="Add a tag and press Enter…"
              className="w-full box-border px-3.5 py-2.5 rounded-xl bg-brand-field text-[13px] mt-1 outline-none focus-visible:ring-2 focus-visible:ring-brand-blue disabled:opacity-50"
            />
          </div>

          {/* Notes */}
          <div className="bg-brand-surface rounded-[22px] p-5.5 shadow-[0_2px_16px_rgba(27,37,89,0.05)] flex flex-col gap-2.5">
            <h2 className="text-[15px] font-extrabold m-0">Your Notes</h2>
            <textarea
              rows={4}
              value={notesDraft}
              onChange={(e) => setNotesDraft(e.target.value)}
              onBlur={handleNotesBlur}
              placeholder="Jot down thoughts on this paper…"
              className="w-full box-border px-3.5 py-3 rounded-2xl bg-brand-field text-[13px] resize-y outline-none focus-visible:ring-2 focus-visible:ring-brand-blue"
            />
          </div>
        </div>
      </div>
    </PageShell>
  );
}