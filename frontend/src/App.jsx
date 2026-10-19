import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { ProtectedRoute } from "./components/ProtectedRoute";
import PapersDashboard from "./pages/PapersDashboard";
import PaperDetail from "./pages/PaperDetail";
import DiscoverPapers from "./pages/DiscoverPapers";
import ResearchChat from "./pages/ResearchChat";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <PapersDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/papers/:id"
        element={
          <ProtectedRoute>
            <PaperDetail />
          </ProtectedRoute>
        }
      />
      <Route
      path="/discover"
      element={
      <ProtectedRoute>
        <DiscoverPapers />
        </ProtectedRoute>
      }
      />
      <Route
      path="/chat"
      element={
      <ProtectedRoute>
        <ResearchChat />
        </ProtectedRoute>
      }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;