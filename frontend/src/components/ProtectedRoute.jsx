import React from "react";
import { useUser } from "../context/UserContext.tsx";
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useUser();
  if (loading) return null; // or a spinner
  if (!user || (allowedRoles && user.roles && !allowedRoles.some(role => user.roles.includes(role)))) {
    return <Navigate to="/login" />;
  }
  return children;
} 