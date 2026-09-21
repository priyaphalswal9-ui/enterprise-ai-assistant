import { useContext } from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  MessageSquare,
  Files,
  Settings,
} from "lucide-react";

import { AuthContext } from "../context/AuthContext";

const navigation = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "AI Assistant",
    path: "/assistant",
    icon: MessageSquare,
  },
  {
    label: "Knowledge",
    path: "/knowledge",
    icon: Files,
  },
  {
    label: "Settings",
    path: "/settings",
    icon: Settings,
  },
];

function Sidebar() {
  const { user } = useContext(AuthContext);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-name">Nexora</div>

        <div className="brand-subtitle">
          AI Knowledge & Workflow Assistant
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigation.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <Icon size={18} strokeWidth={1.8} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

    <div className="sidebar-account">
    <div className="account-avatar">
      {user?.name?.charAt(0).toUpperCase() || "U"}
    </div>

    <div>
      <div className="account-name">
        {user?.name || "User"}
      </div>

      <div className="account-label">
        My Account
      </div>
    </div>
  </div>
    </aside>
  );
}

export default Sidebar;