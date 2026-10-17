import { createContext, useContext, useState } from "react";
import { apiRequest } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));

  const login = async (email, password) => {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);
  };

  const register = async (email, username, password) => {
    await apiRequest("/auth/register", {
      method: "POST",
      body: { email, username, password },
    });
    // doesn't log in automatically — decide below
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}