// ✅ FIXED SOCKET CONNECTION
const socket = io(window.location.origin, {
    transports: ["websocket"]
});

// ---------------- DEPLOY ----------------
async function deploy() {
    const repo = document.getElementById("repo").value;

    const res = await fetch("/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo })
    });

    const data = await res.json();

    if (data.url) {
        alert(`🚀 Deployed successfully!\n${data.url}`);
    }
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

// CPU → update chart
const ctx = document.getElementById("cpuChart").getContext("2d");

const cpuChart = new Chart(ctx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "CPU %",
            data: [],
            borderWidth: 2
        }]
    },
    options: {
        responsive: true
    }
});

socket.on("connect", () => {
    console.log("✅ Socket connected");
});

socket.on("cpu", (data) => {
    cpuChart.data.labels.push("");
    cpuChart.data.datasets[0].data.push(data);

    if (cpuChart.data.labels.length > 20) {
        cpuChart.data.labels.shift();
        cpuChart.data.datasets[0].data.shift();
    }

    cpuChart.update();
});

// Logs
socket.on("logs", (msg) => {
    const logs = document.getElementById("logs");
    logs.textContent += msg;
    logs.scrollTop = logs.scrollHeight;
});

// Alerts
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