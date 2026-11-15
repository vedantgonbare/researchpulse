// src/pages/professor/ProfessorAssignments.jsx
import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { apiRequest } from "../../api/client";
import { PageShell } from "../../components/PageShell";

export default function ProfessorAssignments() {
  const { token } = useAuth();

  // students list, for the picker — same fetch pattern as ProfessorDashboard
  const [students, setStudents] = useState([]);
  const [studentsLoading, setStudentsLoading] = useState(true);
  const [studentsError, setStudentsError] = useState(null);

  // form state — separate from the students-fetch state, same reasoning as the invite form
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [studentId, setStudentId] = useState("");
  const [creating, setCreating] = useState(false);
  const [result, setResult] = useState(null); // { type: "success" | "error", text }

  useEffect(() => {
    async function fetchStudents() {
      try {
        const data = await apiRequest("/professors/students", { token });
        setStudents(data);
      } catch (err) {
        setStudentsError("Could not load your students. Try refreshing.");
      } finally {
        setStudentsLoading(false);
      }
    }
    fetchStudents();
  }, [token]);

  async function handleCreate(e) {
    e.preventDefault();
    setCreating(true);
    setResult(null);

    try {
      const assignment = await apiRequest("/assignments/", {
        method: "POST",
        token,
        body: {
          title,
          description: description || null,
          student_id: Number(studentId),
        },
      });
      setResult({ type: "success", text: `Assignment "${assignment.title}" created.` });
      setTitle("");
      setDescription("");
      setStudentId("");
    } catch (err) {
      setResult({ type: "error", text: err.message || "Could not create assignment." });
    } finally {
      setCreating(false);
    }
  }

  if (studentsLoading) {
    return <PageShell><p className="text-brand-text-muted">Loading your students…</p></PageShell>;
  }

  if (studentsError) {
    return <PageShell><p className="text-brand-text-muted">{studentsError}</p></PageShell>;
  }

  return (
    <PageShell>
      <h1 className="text-xl font-semibold text-brand-navy mb-4">Create assignment</h1>

      {students.length === 0 ? (
        <p className="text-brand-text-muted">
          You don't have any students yet — invite one from the My Students page first.
        </p>
      ) : (
        <form onSubmit={handleCreate} className="flex flex-col gap-4 max-w-xl">
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Assignment title"
            className="rounded-xl border border-brand-border px-4 py-2 bg-brand-field"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description (optional)"
            rows={4}
            className="rounded-xl border border-brand-border px-4 py-2 bg-brand-field"
          />
          <select
            required
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            className="rounded-xl border border-brand-border px-4 py-2 bg-brand-field"
          >
            <option value="" disabled>Select a student</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.username} ({s.email})
              </option>
            ))}
          </select>
          <button
            type="submit"
            disabled={creating}
            className="rounded-xl bg-brand-blue text-white px-4 py-2 disabled:opacity-50 self-start"
          >
            {creating ? "Creating…" : "Create assignment"}
          </button>
        </form>
      )}

      {result && (
        <p className={result.type === "success" ? "text-green-600 mt-4" : "text-red-600 mt-4"}>
          {result.text}
        </p>
      )}
    </PageShell>
  );
}