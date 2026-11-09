// src/context/AuthContext.jsx
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
    // doesn't log in automatically — same contract as registerWithInvite
  };

  const registerWithInvite = async (email, username, password, inviteToken) => {
    await apiRequest("/auth/register-with-invite", {
      method: "POST",
      body: { email, username, password, invite_token: inviteToken },
    });
    // doesn't log in automatically — matches register()'s contract
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{ token, login, register, registerWithInvite, logout, isAuthenticated: !!token }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}