import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import api from "../api/axios";
import { User, AuthToken } from "../models/User";

interface UserContextType {
  user: User | null;
  token: string;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function useUser(): UserContextType {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string>(localStorage.getItem("token") || "");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (token) {
      setLoading(true);
      api
        .get<User>("/api/admin/user/me")
        .then((res) => {
          const userData: User = {
            id: res.data.id,
            username: res.data.username,
            email: res.data.email,
            roles: res.data.roles,
            isActive: res.data.isActive
          };
          setUser(userData);
        })
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

  const login = async (username: string, password: string): Promise<void> => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);
    
    const res = await api.post<AuthToken>("/api/admin/user/login", params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    
    const authToken: AuthToken = res.data;
    setToken(authToken.access_token);
    localStorage.setItem("token", authToken.access_token);
    
    // Fetch user data after successful login
    try {
      const userRes = await api.get<User>("/api/admin/user/me");
      const userData: User = {
        id: userRes.data.id,
        username: userRes.data.username,
        email: userRes.data.email,
        roles: userRes.data.roles,
        isActive: userRes.data.isActive
      };
      setUser(userData);
    } catch (error) {
      // If we can't fetch user data, create a minimal user object
      const userData: User = {
        id: username, // fallback to username as id
        username: username,
        isActive: true
      };
      setUser(userData);
    }
  };

  const logout = (): void => {
    setUser(null);
    setToken("");
    localStorage.removeItem("token");
  };

  const contextValue: UserContextType = {
    user,
    token,
    login,
    logout,
    loading
  };

  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
}
