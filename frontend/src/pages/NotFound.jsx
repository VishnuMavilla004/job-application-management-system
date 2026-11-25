
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <main className="not-found">
      <h1>404</h1>
      <p>This page could not be found.</p>
      <Link to="/login">Return to login</Link>
    </main>
  );
}
