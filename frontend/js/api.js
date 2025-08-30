import { AUTH_API, TASKS_API } from "./config.js";

// Получение токена и обновление при необходимости
async function fetchWithAuth(url, options = {}) {
  let token = localStorage.getItem("access_token");
  options.headers = {
    ...(options.headers || {}),
    Authorization: `Bearer ${token}`,
  };

  let res = await fetch(url, options);

  if (res.status === 401) {
    const refreshed = await refreshToken();
    if (!refreshed) throw new Error("Сессия истекла, войдите снова");

    token = localStorage.getItem("access_token");
    options.headers.Authorization = `Bearer ${token}`;
    res = await fetch(url, options);
  }

  return res;
}

// Обновление токена
export async function refreshToken() {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) {
    console.warn("No refresh token found.");
    return false;
  }

  try {
    const res = await fetch(`${AUTH_API}/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });

    if (!res.ok) {
      console.error("Refresh failed:", res.status);
      return false;
    }

    const data = await res.json();
    console.log("New tokens:", data);

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);

    return true;
  } catch (err) {
    console.error("Error refreshing token:", err);
    return false;
  }
}

// Отправляем GET-запрос (все задачи пользователя)
export async function fetchTasks() {
  try {
    const response = await fetchWithAuth(`${TASKS_API}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Ошибка: ${response.status} ${response.statusText}`);
    }

    const tasks = await response.json();
    console.log("Полученные задачи:", tasks);
    return tasks;
  } catch (error) {
    console.error("Ошибка при получении задач:", error);
    throw error;
  }
}

// Отправляем GET-запрос (определенная задача)
export async function fetchTaskById(taskId) {
  try {
    const url = `${TASKS_API}/${taskId}`;

    const response = await fetchWithAuth(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
    }

    const task = await response.json();
    console.log("Задача:", task);

    return task;
  } catch (error) {
    console.error("Ошибка при получении задачи:", error);
    throw error;
  }
}

// Отправляем POST-запрос
export async function createTask(taskData) {
  try {
    const url = `${TASKS_API}/create`;

    const response = await fetchWithAuth(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
    }

    const newTask = await response.json();
    console.log("Созданная задача:", newTask);

    return newTask;
  } catch (error) {
    console.error("Ошибка при создании задачи:", error);
    throw error;
  }
}

// Отправляем PATCH-запрос (обновление)
export async function updateTaskPartially(taskId, taskData) {
  try {
    const url = `${TASKS_API}/${taskId}`;

    const response = await fetchWithAuth(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log("Результат обновления:", result);

    return result;
  } catch (error) {
    console.error("Ошибка при частичном обновлении задачи:", error);
    throw error;
  }
}

// Отправляем DELETE-запрос
export async function deleteTask(taskId) {
  try {
    const url = `${TASKS_API}/${taskId}`;

    const response = await fetchWithAuth(url, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log("Результат удаления:", result);

    return result;
  } catch (error) {
    console.error("Ошибка при удалении задачи:", error);
    throw error;
  }
}

// Регистрация нового пользователя
export async function registerUser(username, email, password) {
  try {
    const res = await fetch(`${AUTH_API}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, email, password }),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Registration failed");
    }

    const data = await res.json();
    return data; // { id: ..., message: ... }
  } catch (err) {
    throw err;
  }
}

// Вход пользователя в аккаунт
export async function loginUser(username, password) {
  try {
    const res = await fetch(`${AUTH_API}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Login failed");
    }

    return await res.json(); // { access_token, refresh_token, token_type }
  } catch (err) {
    throw err;
  }
}


// logout.js
export async function logoutUser() {
  const token = localStorage.getItem("access_token"); // assuming you stored it here

  if (!token) {
    console.error("No token found!");
    return;
  }

  try {
    const response = await fetch(`${AUTH_API}/login`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Logout failed:", errorData.detail || errorData);
      return;
    }

    const data = await response.json();
    console.log("Logout successful:", data);

    // Optionally clear stored tokens
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    // Redirect user to login page if needed
    window.location.href = "/login.html";

  } catch (error) {
    console.error("Error during logout:", error);
  }
}