// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect  } from "react";
import { apiRequest } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [user, setUser] = useState(null);
  const [userLoading, setUserLoading] = useState(true);

  const fetchCurrentUser = async () => {
    try {
      const data = await apiRequest("/auth/me", { method: "GET", token });
      setUser(data);
    } catch {
      localStorage.removeItem("access_token");
      setToken(null);
      setUser(null);
    } finally {
      setUserLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    } else {
      setUserLoading(false);
    }
  }, [token]);


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
  };

  const registerWithInvite = async (email, username, password, inviteToken) => {
    await apiRequest("/auth/register-with-invite", {
      method: "POST",
      body: { email, username, password, invite_token: inviteToken },
    });
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ token, user, userLoading, login, register, registerWithInvite, logout, isAuthenticated: !!token }}
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