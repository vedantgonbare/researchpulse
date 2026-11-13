import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { ProtectedRoute } from "./components/ProtectedRoute";
import PapersDashboard from "./pages/PapersDashboard";
import PaperDetail from "./pages/PaperDetail";
import DiscoverPapers from "./pages/DiscoverPapers";
import ResearchChat from "./pages/ResearchChat";
import Digest from "./pages/Digest";
import ProfessorDashboard from "./pages/professor/ProfessorDashboard";
import ProfessorAssignments from "./pages/professor/ProfessorAssignments";
import { useAuth } from "./context/AuthContext";
import { getDefaultRouteForRole } from "./utils/roleRoutes";

function CatchAll() {
  const { user } = useAuth();
  return <Navigate to={getDefaultRouteForRole(user?.role)} replace />;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Student routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute requiredRole="student">
            <PapersDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/papers/:id"
        element={
          <ProtectedRoute requiredRole="student">
            <PaperDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/discover"
        element={
          <ProtectedRoute requiredRole="student">
            <DiscoverPapers />
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute requiredRole="student">
            <ResearchChat />
          </ProtectedRoute>
        }
      />
      <Route
        path="/digest"
        element={
          <ProtectedRoute requiredRole="student">
            <Digest />
          </ProtectedRoute>
        }
      />

      {/* Professor routes */}
      <Route
        path="/professor/dashboard"
        element={
          <ProtectedRoute requiredRole="professor">
            <ProfessorDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/professor/assignments"
        element={
          <ProtectedRoute requiredRole="professor">
            <ProfessorAssignments />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<CatchAll />} />
    </Routes>
  );
}

export default App;