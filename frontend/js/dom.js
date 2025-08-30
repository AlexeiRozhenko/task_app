import { createTask, fetchTasks } from "./api.js";

export function renderTasks(tasks) {
  const container = document.getElementById("tasks");
  container.innerHTML = tasks
    .map((task) => {
      // Преобразуем datetime в нужный формат для поля datetime-local
      const formattedDeadline = task.deadline
        ? new Date(task.deadline).toISOString().slice(0, 16) // Преобразуем в ISO и обрезаем лишние части
        : "";

      return `
        <div class="col-lg-3 col-md-4 col-sm-6 task card p-3 mb-2 mx-2">
          <input type="text" class="form-control mb-2 task-title" value="${
            task.title
          }" data-id="${task.id}">
          <textarea class="form-control mb-2 task-content" data-id="${
            task.id
          }">${task.content}</textarea>
          <input type="datetime-local" class="form-control mb-2 task-deadline" value="${formattedDeadline}" data-id="${
        task.id
      }">
          
          <div class="form-check mb-2">
            <input type="checkbox" class="form-check-input task-done" id="done-${
              task.id
            }" data-id="${task.id}" ${task.is_done ? "checked" : ""}>
            <label class="form-check-label" for="done-${task.id}">Done</label>
          </div>

          <div class="d-flex justify-content-between">
            <button data-id="${
              task.id
            }" class="save-btn btn btn-dark btn-sm">Save</button>
            <button data-id="${
              task.id
            }" class="delete-btn btn btn-light btn-sm">Delete</button>
          </div>
        </div>
      `;
    })
    .join("");
}

export function initForm() {
  const form = document.getElementById("taskForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const title = document.getElementById("title").value.trim();
    const content = document.getElementById("content").value.trim();
    const deadline = document.getElementById("deadline").value.trim();

    const taskData = { title, content, deadline };

    try {
      await createTask(taskData);
      renderTasks(await fetchTasks());
      form.reset();
    } catch (err) {
      alert(err.message);
      console.error("Error:", err);
    }
  });
}