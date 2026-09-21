import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useContext } from "react";

import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Assistant from "./pages/Assistant";
import Knowledge from "./pages/Knowledge";
import Settings from "./pages/Settings";
import AuthProvider, { AuthContext } from "./context/AuthContext";

import "./styles/globals.css";
import "./styles/layout.css";
import "./styles/components.css";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useContext(AuthContext);

  if (loading) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />

      <main className="app-main">
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/assistant" element={<Assistant />} />
          <Route path="/knowledge" element={<Knowledge />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          />

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;