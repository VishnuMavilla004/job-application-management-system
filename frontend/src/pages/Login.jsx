
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import AuthLayout from "../layouts/AuthLayout";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (event) => {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await login(form);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(
        err.response?.data?.message ||
        err.response?.data?.detail ||
        "Login failed. Check your credentials."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to continue managing your applications."
    >
      <form onSubmit={handleSubmit} className="auth-form">
        <label htmlFor="email">Email address</label>
        <input
          id="email"
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
          placeholder="you@example.com"
          autoComplete="email"
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          value={form.password}
          onChange={handleChange}
          placeholder="Enter your password"
          autoComplete="current-password"
          required
        />

        {error && <p className="form-error">{error}</p>}

        <button type="submit" disabled={submitting}>
          {submitting ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <p className="auth-switch">
        Don't have an account? <Link to="/register">Create account</Link>
      </p>
    </AuthLayout>
  );
}
