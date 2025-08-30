import { registerUser } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registerForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const result = await registerUser(username, email, password);
      console.log("Success:", result);
      window.location.href = "login.html";
    } catch (err) {
      console.error("Error:", err);
      alert(err.message);
    }
  });
});
