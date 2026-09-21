import apiRequest from "./api";

export async function getConversations() {
  return apiRequest("/conversations");
}