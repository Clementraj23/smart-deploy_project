// ✅ FIXED SOCKET CONNECTION
const socket = io(window.location.origin);

// ---------------- DEPLOY ----------------
async function deploy() {
    const repo = document.getElementById("repo").value;

    await fetch("/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo })
    });
}

// ---------------- LOAD DEPLOYMENTS ----------------
async function loadDeployments() {
    try {
        const res = await fetch("/deployments");
        const data = await res.json();

        const container = document.getElementById("deployments");
        container.innerHTML = "";

        data.forEach(d => {
            const el = document.createElement("div");
            el.innerHTML = `<a href="${d.url}" target="_blank">${d.name}</a>`;
            container.appendChild(el);
        });

    } catch (err) {
        console.error("Error loading deployments", err);
    }
}

// ---------------- SOCKET EVENTS ----------------
socket.on("cpu", (data) => {
    console.log("CPU:", data);
});

socket.on("logs", (msg) => {
    const logs = document.getElementById("logs");
    logs.textContent += msg;
    logs.scrollTop = logs.scrollHeight;
});

socket.on("alert", (msg) => {
    const alerts = document.getElementById("alerts");
    const el = document.createElement("div");
    el.textContent = msg;
    alerts.appendChild(el);
});

// ---------------- AUTO REFRESH ----------------
setInterval(loadDeployments, 5000);

// ---------------- INITIAL LOAD ----------------
loadDeployments();