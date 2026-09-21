import { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  UserRound,
  SlidersHorizontal,
  Shield,
  LogOut,
  ChevronRight,
} from "lucide-react";

import { AuthContext } from "../context/AuthContext";
import { changePassword } from "../services/auth";

import "../styles/settings.css";

function Settings() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [passwordLoading, setPasswordLoading] = useState(false);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  function openPasswordForm() {
    setShowPasswordForm(true);
    setPasswordError("");
    setPasswordSuccess("");
  }

  function closePasswordForm() {
    setShowPasswordForm(false);
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setPasswordError("");
    setPasswordSuccess("");
  }

  async function handleChangePassword(event) {
    event.preventDefault();

    setPasswordError("");
    setPasswordSuccess("");

    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.");
      return;
    }

    setPasswordLoading(true);

    try {
      await changePassword(currentPassword, newPassword);

      setPasswordSuccess("Password changed successfully.");

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      setPasswordError(error.message);
    } finally {
      setPasswordLoading(false);
    }
  }

  return (
    <div className="page-container settings-page">
      <header className="settings-header">
        <p className="eyebrow">SETTINGS</p>

        <h1>Manage your Nexora workspace</h1>

        <p>
          Manage your account, preferences and security settings.
        </p>
      </header>

      <div className="settings-content">
        <section className="settings-section">
          <div className="settings-section-heading">
            <UserRound size={19} strokeWidth={1.7} />

            <div>
              <h2>Account</h2>
              <p>Your account information</p>
            </div>
          </div>

          <div className="settings-list">
            <div className="setting-row">
              <div>
                <span className="setting-label">Name</span>
                <span className="setting-value">
                  {user?.name || "User"}
                </span>
              </div>
            </div>

            <div className="setting-row">
              <div>
                <span className="setting-label">Email</span>
                <span className="setting-value">
                  {user?.email || "—"}
                </span>
              </div>
            </div>

            <div className="setting-row">
              <div>
                <span className="setting-label">Role</span>
                <span className="setting-value">
                  {user?.role || "user"}
                </span>
              </div>
            </div>
          </div>
        </section>

        <section className="settings-section">
          <div className="settings-section-heading">
            <SlidersHorizontal size={19} strokeWidth={1.7} />

            <div>
              <h2>Preferences</h2>
              <p>Control how Nexora behaves</p>
            </div>
          </div>

          <div className="settings-list">
            <div className="setting-row">
              <div>
                <span className="setting-label">Appearance</span>
                <span className="setting-value">
                  System default
                </span>
              </div>
            </div>

            <div className="setting-row">
              <div>
                <span className="setting-label">Language</span>
                <span className="setting-value">
                  English
                </span>
              </div>
            </div>
          </div>
        </section>

        <section className="settings-section">
          <div className="settings-section-heading">
            <Shield size={19} strokeWidth={1.7} />

            <div>
              <h2>Security</h2>
              <p>Manage your account security</p>
            </div>
          </div>

          <div className="settings-list">
            {!showPasswordForm ? (
              <button
                type="button"
                className="setting-row setting-action"
                onClick={openPasswordForm}
              >
                <div>
                  <span className="setting-label">Password</span>
                  <span className="setting-value">
                    Change your password
                  </span>
                </div>

                <ChevronRight size={17} strokeWidth={1.6} />
              </button>
            ) : (
              <form
                className="password-form"
                onSubmit={handleChangePassword}
              >
                <div className="password-form-heading">
                  <h3>Change password</h3>
                  <p>
                    Enter your current password and choose a new one.
                  </p>
                </div>

                <label>
                  Current password
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(event) =>
                      setCurrentPassword(event.target.value)
                    }
                    required
                  />
                </label>

                <label>
                  New password
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(event) =>
                      setNewPassword(event.target.value)
                    }
                    minLength={8}
                    required
                  />
                </label>

                <label>
                  Confirm new password
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(event) =>
                      setConfirmPassword(event.target.value)
                    }
                    minLength={8}
                    required
                  />
                </label>

                {passwordError && (
                  <p className="settings-error">
                    {passwordError}
                  </p>
                )}

                {passwordSuccess && (
                  <p className="settings-success">
                    {passwordSuccess}
                  </p>
                )}

                <div className="password-actions">
                  <button
                    type="submit"
                    className="password-submit"
                    disabled={passwordLoading}
                  >
                    {passwordLoading
                      ? "Updating..."
                      : "Update password"}
                  </button>

                  <button
                    type="button"
                    className="password-cancel"
                    onClick={closePasswordForm}
                    disabled={passwordLoading}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </section>

        <button
          type="button"
          className="logout-button"
          onClick={handleLogout}
        >
          <LogOut size={17} strokeWidth={1.7} />
          Log out
        </button>
      </div>
    </div>
  );
}

export default Settings;