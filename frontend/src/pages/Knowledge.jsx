import { useEffect, useRef, useState } from "react";
import {
  Upload,
  Search,
  FileText,
  MoreHorizontal,
  Trash2,
} from "lucide-react";

import {
  getDocuments,
  uploadDocument,
  deleteDocument,
} from "../services/documents";

import "../styles/knowledge.css";

function Knowledge() {
  const [documents, setDocuments] = useState([]);
  const [loadingDocuments, setLoadingDocuments] =
    useState(true);

  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const [openMenuId, setOpenMenuId] = useState(null);

  const fileInputRef = useRef(null);

  useEffect(() => {
    async function loadDocuments() {
      try {
        const data = await getDocuments();
        setDocuments(data);
      } catch (error) {
        console.error(
          "Failed to load documents:",
          error
        );

        setError("Failed to load documents.");
      } finally {
        setLoadingDocuments(false);
      }
    }

    loadDocuments();
  }, []);

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  async function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploading(true);
    setError("");

    try {
      const uploadedDocument =
        await uploadDocument(file);

      setDocuments((current) => [
        uploadedDocument,
        ...current,
      ]);
    } catch (error) {
      console.error(
        "Failed to upload document:",
        error
      );

      setError(
        error.message ||
          "Failed to upload document."
      );
    } finally {
      setUploading(false);

      // Allow selecting the same file again
      event.target.value = "";
    }
  }

  function handleMenuToggle(documentId) {
    setOpenMenuId((current) =>
      current === documentId
        ? null
        : documentId
    );
  }

  async function handleDeleteDocument(document) {
    setOpenMenuId(null);

    const confirmed = window.confirm(
      `Delete "${document.filename}"?\n\nThis will permanently remove the document and its indexed knowledge.`
    );

    if (!confirmed) {
      return;
    }

    setDeletingId(document.id);
    setError("");

    try {
      await deleteDocument(document.id);

      setDocuments((current) =>
        current.filter(
          (item) => item.id !== document.id
        )
      );
    } catch (error) {
      console.error(
        "Failed to delete document:",
        error
      );

      setError(
        error.message ||
          "Failed to delete document."
      );
    } finally {
      setDeletingId(null);
    }
  }

  const filteredDocuments = documents.filter(
    (document) =>
      document.filename
        ?.toLowerCase()
        .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="knowledge-page">
      <input
        ref={fileInputRef}
        type="file"
        hidden
        onChange={handleFileChange}
      />

      <header className="knowledge-header">
        <div>
          <p className="eyebrow">KNOWLEDGE</p>

          <h1>
            Your organization's knowledge
          </h1>

          <p>
            Upload and manage the documents Nexora
            can use to answer your questions.
          </p>
        </div>

        <button
          className="upload-button"
          type="button"
          onClick={openFilePicker}
          disabled={uploading}
        >
          <Upload
            size={16}
            strokeWidth={1.8}
          />

          {uploading
            ? "Uploading..."
            : "Upload document"}
        </button>
      </header>

      <div className="knowledge-toolbar">
        <div className="knowledge-search">
          <Search
            size={16}
            strokeWidth={1.7}
          />

          <input
            type="text"
            placeholder="Search documents"
            value={searchQuery}
            onChange={(event) =>
              setSearchQuery(event.target.value)
            }
          />
        </div>

        <span className="document-label">
          {documents.length}{" "}
          {documents.length === 1
            ? "Document"
            : "Documents"}
        </span>
      </div>

      {error && (
        <div className="knowledge-error">
          {error}
        </div>
      )}

      <section className="document-list">
        {loadingDocuments ? (
          <div className="document-empty">
            <p>Loading documents...</p>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="document-empty">
            <div className="document-empty-icon">
              <FileText
                size={22}
                strokeWidth={1.5}
              />
            </div>

            <h2>
              {documents.length === 0
                ? "No documents yet"
                : "No matching documents"}
            </h2>

            <p>
              {documents.length === 0
                ? "Upload your first document to start building your knowledge base."
                : "Try a different search term."}
            </p>

            {documents.length === 0 && (
              <button
                className="empty-upload-button"
                type="button"
                onClick={openFilePicker}
                disabled={uploading}
              >
                <Upload
                  size={15}
                  strokeWidth={1.8}
                />

                {uploading
                  ? "Uploading..."
                  : "Upload document"}
              </button>
            )}
          </div>
        ) : (
          <div className="document-items">
            {filteredDocuments.map(
              (document) => (
                <div
                  key={document.id}
                  className="document-row"
                >
                  <div className="document-row-icon">
                    <FileText
                      size={19}
                      strokeWidth={1.6}
                    />
                  </div>

                  <div className="document-row-content">
                    <h3>
                      {document.filename}
                    </h3>

                    <p>
                      {document.file_type ||
                        "Unknown file type"}
                    </p>
                  </div>

                  <div className="document-menu">
                    <button
                      type="button"
                      className="document-menu-button"
                      onClick={() =>
                        handleMenuToggle(
                          document.id
                        )
                      }
                      disabled={
                        deletingId ===
                        document.id
                      }
                      aria-label={`Actions for ${document.filename}`}
                    >
                      <MoreHorizontal
                        size={18}
                        strokeWidth={1.7}
                      />
                    </button>

                    {openMenuId ===
                      document.id && (
                      <div className="document-menu-dropdown">
                        <button
                          type="button"
                          className="document-delete-action"
                          onClick={() =>
                            handleDeleteDocument(
                              document
                            )
                          }
                        >
                          <Trash2
                            size={15}
                            strokeWidth={1.7}
                          />

                          <span>
                            Delete document
                          </span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export default Knowledge;