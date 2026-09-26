import ReactMarkdown from "react-markdown";

function cleanMarkdown(content) {
  if (!content) return "";

  // Backend se escaped markdown aa raha ho to normalize karo
  return content.replace(/\\\*/g, "*");
}

export default function ChatMessage({
  message,
  role,
  content,
  sources = [],
}) {
  const actualRole = role ?? message?.role ?? "assistant";
  const actualContent = content ?? message?.content ?? "";
  const actualSources = sources ?? message?.sources ?? [];

  const isUser = actualRole === "user";

  return (
    <div className={`chat-message ${isUser ? "user-message" : "assistant-message"}`}>
      {!isUser && <div className="message-label">NEXORA</div>}

      <div className="message-content">
        {isUser ? (
          <p>{actualContent}</p>
        ) : (
          <ReactMarkdown
            components={{
              p: ({ children }) => <p>{children}</p>,

              strong: ({ children }) => (
                <strong>{children}</strong>
              ),

              ul: ({ children }) => (
                <ul>{children}</ul>
              ),

              ol: ({ children }) => (
                <ol>{children}</ol>
              ),

              li: ({ children }) => (
                <li>{children}</li>
              ),

              code: ({ inline, children }) =>
                inline ? (
                  <code className="inline-code">{children}</code>
                ) : (
                  <pre className="code-block">
                    <code>{children}</code>
                  </pre>
                ),
            }}
          >
            {cleanMarkdown(actualContent)}
          </ReactMarkdown>
        )}
      </div>

      {!isUser && actualSources.length > 0 && (
        <div className="message-sources">
          <div className="sources-title">Sources</div>

          {actualSources.map((source, index) => (
            <div className="source-item" key={source.id ?? index}>
              <div className="source-name">
                {source.filename ?? source.name ?? "Document"}
              </div>

              {source.chunk_index !== undefined && (
                <div className="source-meta">
                  Section {source.chunk_index + 1}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}