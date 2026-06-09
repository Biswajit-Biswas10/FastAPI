// ═══════════════════════════════════════════════
// TodoApp — Client-Side JavaScript
// ═══════════════════════════════════════════════


// ── Helper Functions ──

function getCookie(name) {
    if (!document.cookie) return null;
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}

function logout() {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        const name = cookies[i].split("=")[0].trim();
        document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
    }
    window.location.href = "/auth/login-page";
}


// ── Login ──

const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(loginForm);
        const payload = new URLSearchParams(formData);

        try {
            const response = await fetch("/auth/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: payload.toString(),
            });

            if (response.ok) {
                const data = await response.json();
                document.cookie = `access_token=${data.access_token}; path=/; SameSite=Lax`;
                window.location.href = "/todos/todo-page";
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Invalid username or password");
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("An error occurred. Please try again.");
        }
    });
}


// ── Registration ──

const registerForm = document.getElementById("registerForm");
if (registerForm) {
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData.entries());

        if (data.password !== data.password2) {
            alert("Passwords do not match");
            return;
        }

        const payload = {
            email: data.email,
            username: data.username,
            first_name: data.firstname,
            last_name: data.lastname,
            role: data.role,
            phone_number: data.phone_number,
            password: data.password,
        };

        try {
            const response = await fetch("/auth/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                alert("Account created successfully! Please login.");
                window.location.href = "/auth/login-page";
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Registration failed. Please try again.");
            }
        } catch (error) {
            console.error("Registration error:", error);
            alert("An error occurred. Please try again.");
        }
    });
}


// ── Add Todo ──

const todoForm = document.getElementById("todoForm");
if (todoForm) {
    todoForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(todoForm);
        const data = Object.fromEntries(formData.entries());

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: false,
        };

        const token = getCookie("access_token");
        if (!token) {
            window.location.href = "/auth/login-page";
            return;
        }

        try {
            const response = await fetch("/todos/todo", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                window.location.href = "/todos/todo-page";
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Failed to create todo.");
            }
        } catch (error) {
            console.error("Create todo error:", error);
            alert("An error occurred. Please try again.");
        }
    });
}


// ── Edit Todo ──

const editTodoForm = document.getElementById("editTodoForm");
if (editTodoForm) {
    editTodoForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(editTodoForm);
        const data = Object.fromEntries(formData.entries());
        const url = window.location.pathname;
        const todoId = url.substring(url.lastIndexOf("/") + 1);

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: data.complete === "on",
        };

        const token = getCookie("access_token");
        if (!token) {
            window.location.href = "/auth/login-page";
            return;
        }

        try {
            const response = await fetch(`/todos/todo/${todoId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                window.location.href = "/todos/todo-page";
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Failed to update todo.");
            }
        } catch (error) {
            console.error("Edit todo error:", error);
            alert("An error occurred. Please try again.");
        }
    });

    // Delete button
    const deleteButton = document.getElementById("deleteButton");
    if (deleteButton) {
        deleteButton.addEventListener("click", async function () {
            if (!confirm("Are you sure you want to delete this todo?")) return;

            const url = window.location.pathname;
            const todoId = url.substring(url.lastIndexOf("/") + 1);

            const token = getCookie("access_token");
            if (!token) {
                window.location.href = "/auth/login-page";
                return;
            }

            try {
                const response = await fetch(`/todos/todo/${todoId}`, {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    window.location.href = "/todos/todo-page";
                } else {
                    const errorData = await response.json();
                    alert(errorData.detail || "Failed to delete todo.");
                }
            } catch (error) {
                console.error("Delete todo error:", error);
                alert("An error occurred. Please try again.");
            }
        });
    }
}