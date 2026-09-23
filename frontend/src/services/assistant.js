const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";


export async function getConversationMessages(
  conversationId
) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_BASE_URL}/conversations/${conversationId}/messages`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load conversation messages"
    );
  }

  return response.json();
}


export async function streamConversationMessage(
  conversationId,
  content,
  documentId,
  { onToken, onSources, onDone }
) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_BASE_URL}/conversations/${conversationId}/messages/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        content,
        document_id: documentId ?? null,
      }),
    }
  );

  if (!response.ok) {
    let detail = "Failed to send message";

    try {
      const errorData = await response.json();

      detail =
        errorData.detail || detail;
    } catch {
      // Keep default error message.
    }

    throw new Error(detail);
  }

  if (!response.body) {
    throw new Error(
      "Streaming is not supported by this response"
    );
  }

  const reader =
    response.body.getReader();

  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { value, done } =
      await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(
      value,
      {
        stream: true,
      }
    );

    const events =
      buffer.split(/\r?\n\r?\n/);

    buffer =
      events.pop() || "";

    for (const eventBlock of events) {
      const lines =
        eventBlock.split(/\r?\n/);

      let eventType = "";
      let data = "";

      for (const line of lines) {
        if (line.startsWith("event:")) {
          eventType =
            line.slice(6).trim();
        }

        if (line.startsWith("data:")) {
          data +=
            line.slice(5).trim();
        }
      }

      if (!data) {
        continue;
      }

      let parsedData;

      try {
        parsedData =
          JSON.parse(data);
      } catch (error) {
        console.error(
          "Failed to parse SSE data:",
          data,
          error
        );

        continue;
      }

      if (eventType === "sources") {
        const receivedSources =
          parsedData.sources;

        console.log(
          "RECEIVED SOURCES:",
          receivedSources
        );

        if (
          Array.isArray(
            receivedSources
          )
        ) {
          onSources?.(
            receivedSources
          );
        } else if (
          receivedSources
        ) {
          onSources?.([
            receivedSources,
          ]);
        } else {
          onSources?.([]);
        }
      }

      if (eventType === "token") {
        onToken?.(
          parsedData.text || ""
        );
      }

      if (eventType === "done") {
        onDone?.(
          parsedData.message_id
        );
      }

      if (eventType === "error") {
        throw new Error(
          parsedData.detail ||
            "AI generation failed"
        );
      }
    }
  }
}