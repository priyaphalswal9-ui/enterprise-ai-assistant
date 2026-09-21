import apiRequest from "./api";

export async function getCurrentUser() {
  return apiRequest("/auth/me");
}

export async function loginUser(email, password) {
  const data = await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
    }),
  });

  localStorage.setItem("access_token", data.access_token);

  return data;
}

export async function registerUser(name, email, password) {
  return apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      name,
      email,
      password,
    }),
  });
}
export async function changePassword(currentPassword, newPassword) {
  return apiRequest("/auth/change-password", {
    method: "POST",
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
}

export function logoutUser() {
  localStorage.removeItem("access_token");
}