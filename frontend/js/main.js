import {
  fetchTasks,
  updateTaskPartially,
  deleteTask,
  logoutUser,
} from "./api.js";

import { renderTasks, initForm } from "./dom.js";

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const tasks = await fetchTasks();
    renderTasks(tasks);
  } catch (err) {
    console.error("Ошибка при загрузке задач:", err);
  }

  // инициализация формы
  initForm();

  // делегирование удаления
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".delete-btn");
    if (btn) {
      try {
        const id = parseInt(btn.dataset.id, 10);
        console.log("Удаляем задачу с id=", id);
        await deleteTask(id);
        renderTasks(await fetchTasks());
      } catch (err) {
        console.error("Ошибка при удалении:", err);
      }
    }
  });
});

// делегирование сохранения
document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".save-btn");
  if (btn) {
    const id = parseInt(btn.dataset.id, 10);

    // читаем значения прямо из DOM
    const title = document
      .querySelector(`.task-title[data-id="${id}"]`)
      .value.trim();
    const content = document
      .querySelector(`.task-content[data-id="${id}"]`)
      .value.trim();
    const deadline = document.querySelector(
      `.task-deadline[data-id="${id}"]`
    ).value;
    const is_done = document.querySelector(
      `.task-done[data-id="${id}"]`
    ).checked;

    const taskData = { title, content, deadline, is_done };

    try {
      await updateTaskPartially(id, taskData);
      alert("Task updated!");
      renderTasks(await fetchTasks());
    } catch (err) {
      console.error("Ошибка при обновлении:", err);
      alert("Не удалось обновить задачу");
    }
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      logoutUser();
      window.location.href = "/login.html";
    });
  }
});
