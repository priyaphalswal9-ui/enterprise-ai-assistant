import { createContext, useEffect, useState } from "react";
import {
  getCurrentUser,
  logoutUser,
} from "../services/auth";

export const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();
          setUser(currentUser.user);
      } catch {
        logoutUser();
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, []);

  function handleLogin(userData) {
    setUser(userData);
  }

  function handleLogout() {
    logoutUser();
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login: handleLogin,
        logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;