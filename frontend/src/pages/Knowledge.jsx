import {
  Upload,
  Search,
  FileText,
  MoreHorizontal,
} from "lucide-react";

import "../styles/knowledge.css";

function Knowledge() {
  return (
    <div className="knowledge-page">
      <header className="knowledge-header">
        <div>
          <p className="eyebrow">KNOWLEDGE</p>
          <h1>Your organization's knowledge</h1>
          <p>
            Upload and manage the documents Nexora can use
            to answer your questions.
          </p>
        </div>

        <button className="upload-button">
          <Upload size={16} strokeWidth={1.8} />
          Upload document
        </button>
      </header>

      <div className="knowledge-toolbar">
        <div className="knowledge-search">
          <Search size={16} strokeWidth={1.7} />
          <input
            type="text"
            placeholder="Search documents"
          />
        </div>

        <span className="document-label">
          Documents
        </span>
      </div>

      <section className="document-list">
        <div className="document-empty">
          <div className="document-empty-icon">
            <FileText size={22} strokeWidth={1.5} />
          </div>

          <h2>No documents yet</h2>

          <p>
            Upload your first document to start building
            your knowledge base.
          </p>

          <button className="empty-upload-button">
            <Upload size={15} strokeWidth={1.8} />
            Upload document
          </button>
        </div>
      </section>
    </div>
  );
}

export default Knowledge;