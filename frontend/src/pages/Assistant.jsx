import {
  MessageSquare,
  Plus,
  Search,
  Paperclip,
  ArrowUp,
} from "lucide-react";

import "../styles/assistant.css";

function Assistant() {
  return (
    <div className="assistant-page">
      <aside className="conversation-panel">
        <div className="conversation-header">
          <div>
            <p className="eyebrow">CONVERSATIONS</p>
            <h1>Assistant</h1>
          </div>

          <button className="new-conversation-button" type="button">
            <Plus size={19} strokeWidth={1.7} />
          </button>
        </div>

        <div className="conversation-search">
          <Search size={17} strokeWidth={1.7} />
          <input
            type="text"
            placeholder="Search conversations"
          />
        </div>

        <div className="conversation-empty">
          <MessageSquare size={22} strokeWidth={1.5} />

          <h2>No conversations yet</h2>

          <p>
            Start a new conversation with Nexora.
          </p>

          <button type="button" className="start-button">
            Start conversation
          </button>
        </div>
      </aside>

      <main className="chat-panel">
        <div className="chat-header">
          <div>
            <p className="eyebrow">NEXORA AI</p>
            <h2>AI Assistant</h2>
          </div>
        </div>

        <div className="chat-content">
          <div className="chat-welcome">
            <div className="welcome-mark">N</div>

            <h1>
              What can I help
              <br />
              you work on?
            </h1>

            <p>
              Ask questions, explore your organization's knowledge,
              or work through a task with Nexora.
            </p>
          </div>
        </div>

        <div className="chat-composer">
          <div className="composer-input">
            <textarea
              placeholder="Ask Nexora..."
              rows={1}
            />

            <div className="composer-actions">
              <button type="button" className="composer-icon">
                <Paperclip size={18} strokeWidth={1.7} />
              </button>

              <button type="button" className="send-button">
                <ArrowUp size={18} strokeWidth={1.8} />
              </button>
            </div>
          </div>

          <p className="composer-note">
            Nexora can use your organization's available knowledge to answer.
          </p>
        </div>
      </main>
    </div>
  );
}

export default Assistant;