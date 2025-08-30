import { loginUser } from './api.js';

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const data = await loginUser(username, password);
      console.log("Login success:", data);

      // Save tokens in localStorage
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      // Redirect to notes page
      window.location.href = "index.html";
    } catch (err) {
      alert(err.message);
      console.error("Login error:", err);
    }
  });
});