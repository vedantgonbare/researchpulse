import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get("invite");

  // Invitation lookup state — separate from the form's own loading/error,
  // since this fetch happens on mount, before the user has done anything.
  const [invitation, setInvitation] = useState(null);
  const [invitationError, setInvitationError] = useState("");
  const [invitationLoading, setInvitationLoading] = useState(!!inviteToken);

  const { register, registerWithInvite } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!inviteToken) return;

    const fetchInvitation = async () => {
      try {
        const res = await fetch(`http://localhost:8000/invitations/${inviteToken}`);
        if (!res.ok) {
          throw new Error(
            res.status === 404 ? "This invitation link is invalid or has expired." : "Could not load invitation."
          );
        }
        const data = await res.json();
        setInvitation(data);
        setEmail(data.student_email); // pre-fill + lock, per the design decision
      } catch (err) {
        setInvitationError(err.message);
      } finally {
        setInvitationLoading(false);
      }
    };

    fetchInvitation();
  }, [inviteToken]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (inviteToken && invitation) {
        await registerWithInvite(email, username, password, inviteToken);
      } else {
        await register(email, username, password);
      }
      navigate("/login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-20 p-6">
      <h1 className="text-2xl font-bold mb-4">Create an account</h1>

      {invitationLoading && (
        <p className="text-sm text-gray-500 mb-4">Checking invitation...</p>
      )}

      {invitationError && (
        <p className="text-sm text-red-600 mb-4 border border-red-200 bg-red-50 rounded px-3 py-2">
          {invitationError}
        </p>
      )}

      {invitation && (
        <p className="text-sm text-blue-800 bg-blue-50 border border-blue-200 rounded px-3 py-2 mb-4">
          You've been invited by <strong>{invitation.professor_name}</strong> ({invitation.professor_email})
        </p>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={!!invitation}
          className="border rounded px-3 py-2 disabled:bg-gray-100 disabled:text-gray-500"
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="border rounded px-3 py-2"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="border rounded px-3 py-2"
        />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading || invitationLoading}
          className="bg-blue-600 text-white rounded px-3 py-2 disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Register"}
        </button>
      </form>
      <p className="mt-4 text-sm">
        Already have an account? <Link to="/login" className="text-blue-600">Log in</Link>
      </p>
    </div>
  );
}