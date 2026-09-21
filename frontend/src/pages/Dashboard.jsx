import {
  ArrowUpRight,
  MessageSquare,
  FileText,
} from "lucide-react";
import { Link } from "react-router-dom";

import "../styles/dashboard.css";

function Dashboard() {
  return (
    <div className="page-container dashboard-page">

      <header className="dashboard-header">
        <div>
          <p className="eyebrow">WORKSPACE</p>

          <h1>Your workspace</h1>

          <p className="dashboard-subtitle">
            Access your conversations and organization knowledge from one place.
          </p>
        </div>
      </header>

      <section className="dashboard-actions">

        <Link to="/assistant" className="dashboard-action-card">
          <div className="dashboard-card-icon">
            <MessageSquare size={19} strokeWidth={1.7} />
          </div>

          <div className="dashboard-card-content">
            <p className="card-label">ASSISTANT</p>

            <h2>Start a conversation</h2>

            <p>
              Ask questions, explore knowledge and work with Nexora.
            </p>
          </div>

          <ArrowUpRight
            className="dashboard-card-arrow"
            size={18}
            strokeWidth={1.6}
          />
        </Link>


        <Link to="/knowledge" className="dashboard-action-card">
          <div className="dashboard-card-icon">
            <FileText size={19} strokeWidth={1.7} />
          </div>

          <div className="dashboard-card-content">
            <p className="card-label">KNOWLEDGE</p>

            <h2>Manage your knowledge</h2>

            <p>
              Upload and manage the documents Nexora can use.
            </p>
          </div>

          <ArrowUpRight
            className="dashboard-card-arrow"
            size={18}
            strokeWidth={1.6}
          />
        </Link>

      </section>


      <section className="dashboard-grid">

        <div className="dashboard-panel">

          <div className="dashboard-panel-header">
            <div>
              <p className="card-label">RECENT ACTIVITY</p>
              <h2>Conversations</h2>
            </div>

            <Link to="/assistant" className="panel-link">
              Open assistant
              <ArrowUpRight size={14} />
            </Link>
          </div>

          <div className="dashboard-empty-state">
            <div className="empty-icon">
              <MessageSquare size={19} strokeWidth={1.6} />
            </div>

            <h3>No conversations yet</h3>

            <p>
              Your recent conversations with Nexora will appear here.
            </p>

            <Link to="/assistant" className="empty-action">
              Start a conversation
              <ArrowUpRight size={14} />
            </Link>
          </div>

        </div>


        <div className="dashboard-panel">

          <div className="dashboard-panel-header">
            <div>
              <p className="card-label">KNOWLEDGE</p>
              <h2>Your documents</h2>
            </div>

            <Link to="/knowledge" className="panel-link">
              View knowledge
              <ArrowUpRight size={14} />
            </Link>
          </div>

          <div className="dashboard-empty-state">
            <div className="empty-icon">
              <FileText size={19} strokeWidth={1.6} />
            </div>

            <h3>No documents yet</h3>

            <p>
              Upload your first document to start building your knowledge base.
            </p>

            <Link to="/knowledge" className="empty-action">
              Add a document
              <ArrowUpRight size={14} />
            </Link>
          </div>

        </div>

      </section>


      <section className="dashboard-footer-card">

        <div>
          <p className="card-label">NEXORA</p>

          <h2>
            Your organization's knowledge, accessible through AI.
          </h2>
        </div>

        <Link to="/assistant" className="footer-card-link">
          Open assistant
          <ArrowUpRight size={15} />
        </Link>

      </section>

    </div>
  );
}

export default Dashboard;