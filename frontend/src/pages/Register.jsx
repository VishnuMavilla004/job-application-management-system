
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import AuthLayout from "../layouts/AuthLayout";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    password_confirm: "",
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

    if (form.password !== form.password_confirm) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);

    try {
      await register(form);
      navigate("/login", { replace: true });
    } catch (err) {
      const data = err.response?.data;
      const message =
        data?.message ||
        data?.detail ||
        (data ? Object.values(data).flat().join(" ") : null);

      setError(message || "Registration failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start organizing your job search today."
    >
      <form onSubmit={handleSubmit} className="auth-form">
        <div className="form-row">
          <div>
            <label htmlFor="first_name">First name</label>
            <input
              id="first_name"
              name="first_name"
              value={form.first_name}
              onChange={handleChange}
              autoComplete="given-name"
              required
            />
          </div>

          <div>
            <label htmlFor="last_name">Last name</label>
            <input
              id="last_name"
              name="last_name"
              value={form.last_name}
              onChange={handleChange}
              autoComplete="family-name"
              required
            />
          </div>
        </div>

        <label htmlFor="email">Email address</label>
        <input
          id="email"
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
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
          autoComplete="new-password"
          required
        />

        <label htmlFor="password_confirm">Confirm password</label>
        <input
          id="password_confirm"
          name="password_confirm"
          type="password"
          value={form.password_confirm}
          onChange={handleChange}
          autoComplete="new-password"
          required
        />

        {error && <p className="form-error">{error}</p>}

        <button type="submit" disabled={submitting}>
          {submitting ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p className="auth-switch">
        Already registered? <Link to="/login">Sign in</Link>
      </p>
    </AuthLayout>
  );
}
