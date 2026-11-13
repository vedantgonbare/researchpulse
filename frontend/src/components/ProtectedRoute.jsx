// src/components/ProtectedRoute.jsx
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getDefaultRouteForRole } from "../utils/roleRoutes";

export function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, user, userLoading } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (userLoading) {
    return null;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to={getDefaultRouteForRole(user?.role)} replace />;
  }

  return children;
}