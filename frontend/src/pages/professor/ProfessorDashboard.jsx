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

  if (loading) {
    return <PageShell><p className="text-brand-text-muted">Loading your students…</p></PageShell>;
  }

  if (error) {
    return <PageShell><p className="text-brand-text-muted">{error}</p></PageShell>;
  }

  return (
    <PageShell>
      <h1 className="text-xl font-semibold text-brand-navy mb-4">My students</h1>
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