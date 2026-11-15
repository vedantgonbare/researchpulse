// src/pages/professor/ProfessorDashboard.jsx
import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { apiRequest } from "../../api/client";
import { PageShell } from "../../components/PageShell";

export default function ProfessorDashboard() {
  const { token } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- invite form state, kept separate from the students-fetch state above ---
  const [email, setEmail] = useState("");
  const [inviting, setInviting] = useState(false);
  const [inviteResult, setInviteResult] = useState(null); // { type: "success" | "error", text: "..." }

  useEffect(() => {
    async function fetchStudents() {
      try {
        const data = await apiRequest("/professors/students", { token });
        setStudents(data);
      } catch (err) {
        setError("Could not load your students. Try refreshing.");
      } finally {
        setLoading(false);
      }
    }
    fetchStudents();
  }, [token]);

  async function handleInvite(e) {
    e.preventDefault(); // stop the browser's default full-page-reload form submit
    setInviting(true);
    setInviteResult(null);

    try {
      await apiRequest("/professors/invite", {
        method: "POST",
        token,
        body: { student_email: email },
      });
      setInviteResult({ type: "success", text: `Invitation sent to ${email}.` });
      setEmail("");
    } catch (err) {
      setInviteResult({ type: "error", text: err.message || "Could not send invitation." });
    } finally {
      setInviting(false);
    }
  }

  if (loading) {
    return <PageShell><p className="text-brand-text-muted">Loading your students…</p></PageShell>;
  }

  if (error) {
    return <PageShell><p className="text-brand-text-muted">{error}</p></PageShell>;
  }

  return (
    <PageShell>
      <h1 className="text-xl font-semibold text-brand-navy mb-4">My students</h1>

      <form onSubmit={handleInvite} className="flex gap-3 mb-6">
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="student@university.edu"
          className="flex-1 rounded-xl border border-brand-border px-4 py-2 bg-brand-field"
        />
        <button
          type="submit"
          disabled={inviting}
          className="rounded-xl bg-brand-blue text-white px-4 py-2 disabled:opacity-50"
        >
          {inviting ? "Sending…" : "Invite student"}
        </button>
      </form>

      {inviteResult && (
        <p className={inviteResult.type === "success" ? "text-green-600 mb-4" : "text-red-600 mb-4"}>
          {inviteResult.text}
        </p>
      )}

      {students.length === 0 ? (
        <p className="text-brand-text-muted">You haven't invited any students yet.</p>
      ) : (
        <ul className="space-y-2">
          {students.map((s) => (
            <li key={s.id} className="bg-brand-surface rounded-xl p-4 shadow-sm flex justify-between">
              <span>{s.username}</span>
              <span className="text-brand-text-muted">{s.email}</span>
            </li>
          ))}
        </ul>
      )}
    </PageShell>
  );
}