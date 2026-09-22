const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

export async function getDocuments() {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_BASE_URL}/documents`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load documents");
  }

  return response.json();
}

export async function uploadDocument(file) {
  const token = localStorage.getItem("access_token");

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }
  );

  if (!response.ok) {
    let detail = "Failed to upload document";

    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch {
      // Keep default error message
    }

    throw new Error(detail);
  }

  return response.json();
}

export async function deleteDocument(documentId) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}`,
    {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    let detail = "Failed to delete document";

    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch {
      // Keep default error message
    }

    throw new Error(detail);
  }

  return response.json();
}