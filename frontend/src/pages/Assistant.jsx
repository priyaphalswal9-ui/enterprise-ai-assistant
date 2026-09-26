import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

import {
  MessageSquare,
  Plus,
  Search,
  Paperclip,
  ArrowUp,
  FileText,
  Check,
  MoreHorizontal,
  Trash2,
} from "lucide-react";

import {
  getConversations,
  createConversation,
  deleteConversation,
} from "../services/conversations";

import {
  getConversationMessages,
  streamConversationMessage,
} from "../services/assistant";

import { uploadDocument } from "../services/documents";

import "../styles/assistant.css";


function Assistant() {
  const [conversations, setConversations] = useState([]);
  const [loadingConversations, setLoadingConversations] =
    useState(true);

  const [selectedConversationId, setSelectedConversationId] =
    useState(null);

  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);

  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const [sources, setSources] = useState([]);

  const [uploadingFile, setUploadingFile] = useState(false);
  const [attachedFile, setAttachedFile] = useState(null);

  const [openMenuId, setOpenMenuId] = useState(null);
  const [deletingConversationId, setDeletingConversationId] =
    useState(null);

  const [conversationSearch, setConversationSearch] =
    useState("");

  const [sendError, setSendError] = useState("");

  const fileInputRef = useRef(null);


  useEffect(() => {
    async function loadConversations() {
      try {
        const data = await getConversations();
        setConversations(data);
      } catch (error) {
        console.error(
          "Failed to load conversations:",
          error
        );
      } finally {
        setLoadingConversations(false);
      }
    }

    loadConversations();
  }, []);


  async function handleNewConversation() {
    try {
      const conversation = await createConversation();

      setConversations((current) => [
        conversation,
        ...current,
      ]);

      setSelectedConversationId(conversation.id);
      setMessages([]);
      setSources([]);
      setInput("");
      setAttachedFile(null);
      setOpenMenuId(null);
      setConversationSearch("");
      setSendError("");
    } catch (error) {
      console.error(
        "Failed to create conversation:",
        error
      );

      alert(
        error.message ||
          "Failed to create conversation."
      );
    }
  }


  async function handleSelectConversation(
    conversationId
  ) {
    setSelectedConversationId(conversationId);
    setLoadingMessages(true);
    setSources([]);
    setAttachedFile(null);
    setOpenMenuId(null);
    setSendError("");

    try {
      const data =
        await getConversationMessages(
          conversationId
        );

      setMessages(data);
    } catch (error) {
      console.error(
        "Failed to load conversation messages:",
        error
      );

      setMessages([]);

      setSendError(
        error.message ||
          "Failed to load this conversation."
      );
    } finally {
      setLoadingMessages(false);
    }
  }


  async function handleDeleteConversation(
    conversation
  ) {
    setOpenMenuId(null);

    const confirmed = window.confirm(
      `Delete "${
        conversation.title ||
        "Untitled conversation"
      }"?\n\nThis will permanently delete the conversation and its messages.`
    );

    if (!confirmed) {
      return;
    }

    setDeletingConversationId(
      conversation.id
    );

    try {
      await deleteConversation(
        conversation.id
      );

      setConversations((current) =>
        current.filter(
          (item) =>
            item.id !== conversation.id
        )
      );

      if (
        selectedConversationId ===
        conversation.id
      ) {
        setSelectedConversationId(null);
        setMessages([]);
        setSources([]);
        setInput("");
        setAttachedFile(null);
        setSendError("");
      }
    } catch (error) {
      console.error(
        "Failed to delete conversation:",
        error
      );

      alert(
        error.message ||
          "Failed to delete conversation."
      );
    } finally {
      setDeletingConversationId(null);
    }
  }


  function openFilePicker() {
    if (uploadingFile || sending) {
      return;
    }

    fileInputRef.current?.click();
  }


  async function handleFileChange(event) {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploadingFile(true);
    setSendError("");

    try {
      const uploadedDocument =
        await uploadDocument(file);

      setAttachedFile(
        uploadedDocument
      );
    } catch (error) {
      console.error(
        "Failed to upload document:",
        error
      );

      setSendError(
        error.message ||
          "Failed to upload document."
      );
    } finally {
      setUploadingFile(false);
      event.target.value = "";
    }
  }


  async function handleSendMessage() {
    const content = input.trim();

    if (!content) {
      return;
    }

    if (!selectedConversationId) {
      return;
    }

    if (sending) {
      return;
    }

    setSendError("");

    const documentId =
      attachedFile?.id ??
      attachedFile?.document_id ??
      null;

    const userMessage = {
      id: `temp-user-${Date.now()}`,
      conversation_id:
        selectedConversationId,
      role: "user",
      content,
      created_at:
        new Date().toISOString(),
    };

    const assistantMessageId =
      `temp-assistant-${Date.now()}`;

    const assistantMessage = {
      id: assistantMessageId,
      conversation_id:
        selectedConversationId,
      role: "assistant",
      content: "",
      created_at:
        new Date().toISOString(),
    };

    setMessages((current) => [
      ...current,
      userMessage,
      assistantMessage,
    ]);

    setSources([]);
    setInput("");
    setSending(true);

    try {
      await streamConversationMessage(
        selectedConversationId,
        content,
        documentId,
        {
          onToken: (token) => {
            setMessages((current) =>
              current.map((message) =>
                message.id ===
                assistantMessageId
                  ? {
                      ...message,
                      content:
                        message.content +
                        token,
                    }
                  : message
              )
            );
          },

          onSources: (
            receivedSources
          ) => {
            setSources(
              receivedSources
            );
          },

          onDone: () => {},
        }
      );

      const updatedMessages =
        await getConversationMessages(
          selectedConversationId
        );

      setMessages(
        updatedMessages
      );

      const updatedConversations =
        await getConversations();

      setConversations(
        updatedConversations
      );

      setAttachedFile(null);
    } catch (error) {
      console.error(
        "Failed to send message:",
        error
      );

      setMessages((current) =>
        current.map((message) =>
          message.id ===
          assistantMessageId
            ? {
                ...message,
                content: "",
              }
            : message
        )
      );

      setSendError(
        error.message ||
          "Something went wrong while generating the response."
      );
    } finally {
      setSending(false);
    }
  }


  function handleInputKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      handleSendMessage();
    }
  }


  function getSourceTitle(
    source,
    index
  ) {
    return (
      source.title ||
      source.document_name ||
      source.document ||
      source.filename ||
      source.file_name ||
      `Source ${index + 1}`
    );
  }


  function getSourceText(source) {
    return (
      source.content ||
      source.text ||
      source.chunk ||
      source.snippet ||
      ""
    );
  }


  /*
   * The backend may return escaped markdown
   * in some responses. Only normalize escaped
   * asterisks so markdown such as **bold**
   * can render correctly.
   */
  function normalizeMarkdown(content) {
    if (!content) {
      return "";
    }

    return content.replace(/\\\*/g, "*");
  }


  const filteredConversations =
    conversations.filter(
      (conversation) => {
        const title =
          conversation.title ||
          "Untitled conversation";

        return title
          .toLowerCase()
          .includes(
            conversationSearch.toLowerCase()
          );
      }
    );


  const uniqueSources =
    sources.filter(
      (source, index, array) => {
        const currentTitle =
          getSourceTitle(
            source,
            index
          );

        return (
          array.findIndex(
            (
              item,
              itemIndex
            ) =>
              getSourceTitle(
                item,
                itemIndex
              ) === currentTitle
          ) === index
        );
      }
    );


  return (
    <div className="assistant-page">

      <aside className="conversation-panel">
        <div className="conversation-header">
          <div>
            <p className="eyebrow">
              CONVERSATIONS
            </p>

            <h1>Assistant</h1>
          </div>

          <button
            className="new-conversation-button"
            type="button"
            onClick={
              handleNewConversation
            }
            aria-label="New conversation"
          >
            <Plus
              size={19}
              strokeWidth={1.7}
            />
          </button>
        </div>


        <div className="conversation-search">
          <Search
            size={17}
            strokeWidth={1.7}
          />

          <input
            type="text"
            placeholder="Search conversations"
            value={
              conversationSearch
            }
            onChange={(event) =>
              setConversationSearch(
                event.target.value
              )
            }
          />
        </div>


        {loadingConversations ? (
          <div className="conversation-empty">
            <p>
              Loading conversations...
            </p>
          </div>
        ) : conversations.length ===
          0 ? (
          <div className="conversation-empty">
            <MessageSquare
              size={22}
              strokeWidth={1.5}
            />

            <h2>
              No conversations yet
            </h2>

            <p>
              Start a new conversation
              with Nexora.
            </p>

            <button
              type="button"
              className="start-button"
              onClick={
                handleNewConversation
              }
            >
              Start conversation
            </button>
          </div>
        ) : filteredConversations.length ===
          0 ? (
          <div className="conversation-empty">
            <Search
              size={22}
              strokeWidth={1.5}
            />

            <h2>
              No matching
              conversations
            </h2>

            <p>
              Try a different search
              term.
            </p>
          </div>
        ) : (
          <div className="conversation-list">
            {filteredConversations.map(
              (conversation) => (
                <div
                  key={
                    conversation.id
                  }
                  className={`conversation-item-wrapper ${
                    selectedConversationId ===
                    conversation.id
                      ? "active"
                      : ""
                  }`}
                >
                  <button
                    type="button"
                    className="conversation-item"
                    onClick={() =>
                      handleSelectConversation(
                        conversation.id
                      )
                    }
                  >
                    <MessageSquare
                      size={16}
                      strokeWidth={1.6}
                    />

                    <span>
                      {conversation.title ||
                        "Untitled conversation"}
                    </span>
                  </button>


                  <button
                    type="button"
                    className="conversation-menu-button"
                    onClick={(event) => {
                      event.stopPropagation();

                      setOpenMenuId(
                        (current) =>
                          current ===
                          conversation.id
                            ? null
                            : conversation.id
                      );
                    }}
                    disabled={
                      deletingConversationId ===
                      conversation.id
                    }
                    aria-label={`Actions for ${
                      conversation.title ||
                      "conversation"
                    }`}
                  >
                    <MoreHorizontal
                      size={16}
                      strokeWidth={1.7}
                    />
                  </button>


                  {openMenuId ===
                    conversation.id && (
                    <div className="conversation-menu-dropdown">
                      <button
                        type="button"
                        className="conversation-delete-action"
                        onClick={() =>
                          handleDeleteConversation(
                            conversation
                          )
                        }
                      >
                        <Trash2
                          size={14}
                          strokeWidth={1.7}
                        />

                        <span>
                          Delete conversation
                        </span>
                      </button>
                    </div>
                  )}
                </div>
              )
            )}
          </div>
        )}
      </aside>


      <main className="chat-panel">

        <div className="chat-header">
          <div>
            <p className="eyebrow">
              NEXORA AI
            </p>

            <h2>
              AI Assistant
            </h2>
          </div>
        </div>


        <div className="chat-content">

          {!selectedConversationId ? (
            <div className="chat-welcome">
              <div className="welcome-mark">
                N
              </div>

              <h1>
                What can I help
                <br />
                you work on?
              </h1>

              <p>
                Ask questions, explore
                your organization's
                knowledge, or work
                through a task with
                Nexora.
              </p>
            </div>

          ) : loadingMessages ? (

            <div className="chat-welcome">
              <p>
                Loading conversation...
              </p>
            </div>

          ) : messages.length ===
            0 ? (

            <div className="chat-welcome">
              <div className="welcome-mark">
                N
              </div>

              <h1>
                Start a conversation
              </h1>

              <p>
                Ask Nexora something
                about your
                organization's
                knowledge.
              </p>
            </div>

          ) : (

            <div className="message-list">

              {messages.map(
                (message) => (
                  <div
                    key={message.id}
                    className={`chat-message ${
                      message.role ===
                      "user"
                        ? "user-message"
                        : "assistant-message"
                    }`}
                  >

                    <div className="message-role">
                      <span>
                        {message.role ===
                        "user"
                          ? "You"
                          : "Nexora"}
                      </span>
                    </div>


                    <div className="message-content">

                      {message.role ===
                      "assistant" ? (
                        <ReactMarkdown
                          components={{
                            p: ({
                              children,
                            }) => (
                              <p>
                                {children}
                              </p>
                            ),

                            strong: ({
                              children,
                            }) => (
                              <strong>
                                {children}
                              </strong>
                            ),

                            em: ({
                              children,
                            }) => (
                              <em>
                                {children}
                              </em>
                            ),

                            ul: ({
                              children,
                            }) => (
                              <ul>
                                {children}
                              </ul>
                            ),

                            ol: ({
                              children,
                            }) => (
                              <ol>
                                {children}
                              </ol>
                            ),

                            li: ({
                              children,
                            }) => (
                              <li>
                                {children}
                              </li>
                            ),

                            blockquote: ({
                              children,
                            }) => (
                              <blockquote>
                                {children}
                              </blockquote>
                            ),

                            code: ({
                              className,
                              children,
                            }) => {
                              const isBlock =
                                Boolean(
                                  className
                                );

                              if (
                                isBlock
                              ) {
                                return (
                                  <pre className="markdown-code-block">
                                    <code
                                      className={
                                        className
                                      }
                                    >
                                      {
                                        children
                                      }
                                    </code>
                                  </pre>
                                );
                              }

                              return (
                                <code className="markdown-inline-code">
                                  {
                                    children
                                  }
                                </code>
                              );
                            },
                          }}
                        >
                          {normalizeMarkdown(
                            message.content
                          )}
                        </ReactMarkdown>

                      ) : (

                        <p>
                          {message.content}
                        </p>

                      )}

                    </div>

                  </div>
                )
              )}


              {sending && (
                <div className="message-status">
                  <span className="status-dot" />
                  Nexora is responding
                </div>
              )}


              {uniqueSources.length >
                0 && (
                <div className="sources-section">

                  <div className="sources-header">
                    <FileText
                      size={15}
                      strokeWidth={1.7}
                    />

                    <span>
                      Sources used
                    </span>
                  </div>


                  <div className="sources-list">

                    {uniqueSources.map(
                      (
                        source,
                        index
                      ) => (
                        <div
                          className="source-card"
                          key={
                            source.id ||
                            source.document_id ||
                            getSourceTitle(
                              source,
                              index
                            )
                          }
                        >

                          <div className="source-icon">
                            <FileText
                              size={15}
                              strokeWidth={1.6}
                            />
                          </div>


                          <div className="source-info">

                            <p className="source-title">
                              {getSourceTitle(
                                source,
                                index
                              )}
                            </p>


                            {getSourceText(
                              source
                            ) && (
                              <p className="source-preview">
                                {getSourceText(
                                  source
                                )}
                              </p>
                            )}

                          </div>

                        </div>
                      )
                    )}

                  </div>

                </div>
              )}


              {sendError && (
                <div className="message-error">
                  <span>
                    {sendError}
                  </span>

                  <button
                    type="button"
                    onClick={() =>
                      setSendError(
                        ""
                      )
                    }
                  >
                    Dismiss
                  </button>
                </div>
              )}

            </div>
          )}

        </div>


        <div className="chat-composer">

          {attachedFile && (
            <div className="attached-file">
              <div className="attached-file-info">

                <FileText
                  size={15}
                  strokeWidth={1.7}
                />

                <span>
                  {attachedFile.filename ||
                    attachedFile.file_name ||
                    "Document added"}
                </span>

                <Check
                  size={14}
                  strokeWidth={2}
                />

              </div>
            </div>
          )}


          <div className="composer-input">

            <textarea
              placeholder={
                selectedConversationId
                  ? "Ask Nexora..."
                  : "Select or create a conversation..."
              }
              rows={1}
              value={input}
              onChange={(event) =>
                setInput(
                  event.target.value
                )
              }
              onKeyDown={
                handleInputKeyDown
              }
              disabled={
                !selectedConversationId ||
                sending ||
                uploadingFile
              }
            />


            <div className="composer-actions">

              <input
                ref={fileInputRef}
                type="file"
                hidden
                onChange={
                  handleFileChange
                }
              />


              <button
                type="button"
                className="composer-icon"
                onClick={
                  openFilePicker
                }
                disabled={
                  uploadingFile ||
                  sending ||
                  !selectedConversationId
                }
                title="Add document"
                aria-label="Add document"
              >
                <Paperclip
                  size={18}
                  strokeWidth={1.7}
                />
              </button>


              <button
                type="button"
                className="send-button"
                onClick={
                  handleSendMessage
                }
                disabled={
                  !selectedConversationId ||
                  !input.trim() ||
                  sending ||
                  uploadingFile
                }
                aria-label="Send message"
              >
                <ArrowUp
                  size={18}
                  strokeWidth={1.8}
                />
              </button>

            </div>

          </div>


          <p className="composer-note">
            {uploadingFile
              ? "Adding document to your knowledge..."
              : attachedFile
                ? "Document added to your knowledge. Ask Nexora about it."
                : "Nexora can use your organization's available knowledge to answer."}
          </p>

        </div>

      </main>

    </div>
  );
}


export default Assistant;