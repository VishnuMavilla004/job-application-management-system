import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/auth/ProtectedRoute";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";

function DashboardPlaceholder() {
  const { user, logout } = useAuth();

  return (
    <main className="placeholder-page">
      <h1>Authentication successful</h1>
      <p>Welcome, {user?.first_name || user?.email}.</p>
      <p>Your protected dashboard will be implemented in Phase 11.</p>
      <button onClick={logout}>Logout</button>
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}