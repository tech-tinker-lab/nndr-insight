import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../api/axios";

const UserContext = createContext();

export function useUser() {
  return useContext(UserContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      setLoading(true);
      api
        .get("/api/admin/user/me")
        .then((res) => setUser(res.data))
        .catch(() => {
          setUser(null);
          setToken("");
          localStorage.removeItem("token");
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);
    const res = await api.post("/api/admin/user/login", params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    setToken(res.data.access_token);
    localStorage.setItem("token", res.data.access_token);
    setUser({ ...res.data, username });
  };

  const logout = () => {
    setUser(null);
    setToken("");
    localStorage.removeItem("token");
  };

  return (
    <UserContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </UserContext.Provider>
  );
} 