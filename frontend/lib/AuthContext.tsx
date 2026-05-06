"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

type User = {
  id: string;
  name: string;
  role: "employee" | "manager" | "admin";
};

type AuthContextType = {
  user: User | null;
  login: (role: "employee" | "manager") => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  // Load user from local storage on mount
  useEffect(() => {
    const stored = localStorage.getItem("assistant_user");
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const login = (role: "employee" | "manager") => {
    const mockUser: User = {
      id: role === "manager" ? "manager-123" : "emp-456",
      name: role === "manager" ? "Alice (Manager)" : "Bob (Employee)",
      role: role,
    };
    setUser(mockUser);
    localStorage.setItem("assistant_user", JSON.stringify(mockUser));
    router.push("/chat");
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("assistant_user");
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};