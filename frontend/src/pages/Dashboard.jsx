import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  MessageSquare,
  FileText,
} from "lucide-react";
import { Link } from "react-router-dom";

import { getConversations } from "../services/conversations";
import { getDocuments } from "../services/documents";

import "../styles/dashboard.css";

function Dashboard() {
  const [conversations, setConversations] = useState([]);
  const [documents, setDocuments] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        setError("");

        const [conversationData, documentData] =
          await Promise.all([
            getConversations(),
            getDocuments(),
          ]);

        setConversations(
          Array.isArray(conversationData)
            ? conversationData
            : []
        );

        setDocuments(
          Array.isArray(documentData)
            ? documentData
            : []
        );
      } catch (error) {
        console.error(
          "Failed to load dashboard data:",
          error
        );

        setError(
          error.message ||
            "Failed to load workspace data."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  const recentConversations =
    conversations.slice(0, 5);

  const recentDocuments =
    documents.slice(0, 5);

  return (
    <div className="page-container dashboard-page">

      <header className="dashboard-header">
        <div>
          <p className="eyebrow">WORKSPACE</p>

          <h1>Your workspace</h1>

          <p className="dashboard-subtitle">
            Access your conversations and organization
            knowledge from one place.
          </p>
        </div>
      </header>


      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}


      <section className="dashboard-actions">

        <Link
          to="/assistant"
          className="dashboard-action-card"
        >
          <div className="dashboard-card-icon">
            <MessageSquare
              size={19}
              strokeWidth={1.7}
            />
          </div>

          <div className="dashboard-card-content">
            <p className="card-label">ASSISTANT</p>

            <h2>Start a conversation</h2>

            <p>
              Ask questions, explore knowledge and work
              with Nexora.
            </p>
          </div>

          <ArrowUpRight
            className="dashboard-card-arrow"
            size={18}
            strokeWidth={1.6}
          />
        </Link>


        <Link
          to="/knowledge"
          className="dashboard-action-card"
        >
          <div className="dashboard-card-icon">
            <FileText
              size={19}
              strokeWidth={1.7}
            />
          </div>

          <div className="dashboard-card-content">
            <p className="card-label">KNOWLEDGE</p>

            <h2>Manage your knowledge</h2>

            <p>
              Upload and manage the documents Nexora
              can use.
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

        {/* Conversations */}

        <div className="dashboard-panel">

          <div className="dashboard-panel-header">
            <div>
              <p className="card-label">
                RECENT ACTIVITY
              </p>

              <h2>
                Conversations
                {!loading &&
                  ` · ${conversations.length}`}
              </h2>
            </div>

            <Link
              to="/assistant"
              className="panel-link"
            >
              Open assistant
              <ArrowUpRight size={14} />
            </Link>
          </div>


          {loading ? (
            <div className="dashboard-empty-state">
              <p>Loading conversations...</p>
            </div>
          ) : recentConversations.length === 0 ? (
            <div className="dashboard-empty-state">

              <div className="empty-icon">
                <MessageSquare
                  size={19}
                  strokeWidth={1.6}
                />
              </div>

              <h3>No conversations yet</h3>

              <p>
                Your recent conversations with Nexora
                will appear here.
              </p>

              <Link
                to="/assistant"
                className="empty-action"
              >
                Start a conversation
                <ArrowUpRight size={14} />
              </Link>

            </div>
          ) : (
            <div className="dashboard-list">

              {recentConversations.map(
                (conversation) => (
                  <Link
                    key={conversation.id}
                    to="/assistant"
                    className="dashboard-list-item"
                  >
                    <div className="dashboard-list-icon">
                      <MessageSquare
                        size={16}
                        strokeWidth={1.6}
                      />
                    </div>

                    <div className="dashboard-list-content">
                      <p>
                        {conversation.title ||
                          "Untitled conversation"}
                      </p>

                      <span>
                        Conversation
                      </span>
                    </div>

                    <ArrowUpRight
                      size={15}
                      strokeWidth={1.6}
                    />
                  </Link>
                )
              )}

            </div>
          )}

        </div>


        {/* Documents */}

        <div className="dashboard-panel">

          <div className="dashboard-panel-header">
            <div>
              <p className="card-label">
                KNOWLEDGE
              </p>

              <h2>
                Your documents
                {!loading &&
                  ` · ${documents.length}`}
              </h2>
            </div>

            <Link
              to="/knowledge"
              className="panel-link"
            >
              View knowledge
              <ArrowUpRight size={14} />
            </Link>
          </div>


          {loading ? (
            <div className="dashboard-empty-state">
              <p>Loading documents...</p>
            </div>
          ) : recentDocuments.length === 0 ? (
            <div className="dashboard-empty-state">

              <div className="empty-icon">
                <FileText
                  size={19}
                  strokeWidth={1.6}
                />
              </div>

              <h3>No documents yet</h3>

              <p>
                Upload your first document to start
                building your knowledge base.
              </p>

              <Link
                to="/knowledge"
                className="empty-action"
              >
                Add a document
                <ArrowUpRight size={14} />
              </Link>

            </div>
          ) : (
            <div className="dashboard-list">

              {recentDocuments.map((document) => (
                <Link
                  key={document.id}
                  to="/knowledge"
                  className="dashboard-list-item"
                >
                  <div className="dashboard-list-icon">
                    <FileText
                      size={16}
                      strokeWidth={1.6}
                    />
                  </div>

                  <div className="dashboard-list-content">
                    <p>
                      {document.filename ||
                        document.file_name ||
                        document.name ||
                        "Untitled document"}
                    </p>

                    <span>
                      Knowledge document
                    </span>
                  </div>

                  <ArrowUpRight
                    size={15}
                    strokeWidth={1.6}
                  />
                </Link>
              ))}

            </div>
          )}

        </div>

      </section>


      <section className="dashboard-footer-card">

        <div>
          <p className="card-label">NEXORA</p>

          <h2>
            Your organization's knowledge,
            accessible through AI.
          </h2>
        </div>

        <Link
          to="/assistant"
          className="footer-card-link"
        >
          Open assistant
          <ArrowUpRight size={15} />
        </Link>

      </section>

    </div>
  );
}

export default Dashboard;