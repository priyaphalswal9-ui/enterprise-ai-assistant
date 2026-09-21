import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";

import { registerUser } from "../services/auth";

import "../styles/auth.css";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await registerUser(name, email, password);

      setSuccess("Account created successfully. You can now sign in.");

      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <div className="brand-name">NEXORA</div>
        <p>AI KNOWLEDGE & WORKFLOW ASSISTANT</p>
      </div>

      <main className="auth-card">
        <div className="auth-heading">
          <p className="eyebrow">GET STARTED</p>

          <h1>Create your account</h1>

          <p>
            Create your Nexora workspace and start working
            with your organization's knowledge.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Name

            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Your name"
              required
            />
          </label>

          <label>
            Email

            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@organization.com"
              required
            />
          </label>

          <label>
            Password

            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Create a password"
              required
            />
          </label>

          {error && (
            <p className="auth-error">
              {error}
            </p>
          )}

          {success && (
            <p className="auth-success">
              {success}
            </p>
          )}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? "Creating account..." : "Create account"}

            {!loading && (
              <ArrowRight size={16} strokeWidth={1.8} />
            )}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account?{" "}
          <Link to="/login">Sign in</Link>
        </p>
      </main>
    </div>
  );
}

export default Register;