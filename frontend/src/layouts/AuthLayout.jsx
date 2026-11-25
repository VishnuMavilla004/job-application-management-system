
import { BriefcaseBusiness } from "lucide-react";
import "../styles/auth.css";

export default function AuthLayout({ children, title, subtitle }) {
  return (
    <main className="auth-page">
      <section className="auth-brand-panel">
        <div className="brand">
          <BriefcaseBusiness size={28} />
          <span>CareerTrack</span>
        </div>

        <div className="brand-content">
          <p className="eyebrow">YOUR CAREER, ORGANIZED</p>
          <h1>Take control of your job search.</h1>
          <p>
            Track applications, manage interviews, and keep every
            opportunity organized in one place.
          </p>
        </div>

        <p className="brand-footer">
          Job Application Management System
        </p>
      </section>

      <section className="auth-form-panel">
        <div className="auth-card">
          <h2>{title}</h2>
          <p className="auth-subtitle">{subtitle}</p>
          {children}
        </div>
      </section>
    </main>
  );
}
