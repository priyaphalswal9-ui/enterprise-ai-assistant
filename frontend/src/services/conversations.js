import apiRequest from "./api";

export async function getConversations() {
  return apiRequest("/conversations");
}

export async function createConversation(
  title = "New conversation"
) {
  return apiRequest("/conversations", {
    method: "POST",
    body: JSON.stringify({
      title,
    }),
  });
}

export async function deleteConversation(conversationId) {
  return apiRequest(
    `/conversations/${conversationId}`,
    {
      method: "DELETE",
    }
  );
}