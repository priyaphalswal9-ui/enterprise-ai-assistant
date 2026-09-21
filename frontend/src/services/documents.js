import apiRequest from "./api";

export async function getDocuments() {
  return apiRequest("/documents");
}