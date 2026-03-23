// ================= SOCKET CONNECTION =================
const socket = io({
    transports: ["websocket", "polling"]
});

// ================= DOM ELEMENTS =================
const cpuText = document.getElementById("cpu");
const logsBox = document.getElementById("logs");
const deployList = document.getElementById("deployments");

// ================= CPU GRAPH =================
const ctx = document.getElementById("cpuChart").getContext("2d");

let cpuData = [];
let labels = [];

const cpuChart = new Chart(ctx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [{
            label: "CPU Usage (%)",
            data: cpuData,
            borderWidth: 2,
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        animation: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});

// ================= SOCKET EVENTS =================

// 🔌 Connected
socket.on("connect", () => {
    console.log("✅ Connected to server");
});

// 📊 CPU UPDATE
socket.on("cpu", (value) => {
    cpuText.innerText = `CPU: ${value}%`;

    // Update graph
    if (cpuData.length > 20) {
        cpuData.shift();
        labels.shift();
    }

    cpuData.push(value);
    labels.push("");

    cpuChart.update();
});

// 🚨 ALERT
socket.on("alert", (msg) => {
    alert(msg);
});

// 📜 LOG STREAM
socket.on("log", (msg) => {
    logsBox.innerText += msg + "\n";
    logsBox.scrollTop = logsBox.scrollHeight;
});

// ================= DEPLOY FUNCTION =================
async function deployRepo() {
    const repo = document.getElementById("repo").value;

    if (!repo) {
        alert("Enter GitHub Repo URL");
        return;
    }

    try {
        const res = await fetch("/deploy", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ repo })
        });

        const data = await res.json();

        if (data.error) {
            alert(data.error);
        } else {
            alert("🚀 Deployed: " + data.url);
            loadDeployments();
        }

    } catch (err) {
        console.error(err);
        alert("Deployment failed");
    }
}

// ================= LOAD DEPLOYMENTS =================
async function loadDeployments() {
    try {
        const res = await fetch("/deployments");
        const data = await res.json();

        deployList.innerHTML = "";

        data.forEach(d => {
            const div = document.createElement("div");

            div.innerHTML = `
                <p><b>${d.repo}</b></p>
                <a href="${d.url}" target="_blank">${d.url}</a>
                <hr/>
            `;

            deployList.appendChild(div);
        });

    } catch (err) {
        console.error("Error loading deployments", err);
    }
}

// ================= AUTO REFRESH =================
setInterval(loadDeployments, 5000);

// ================= INITIAL LOAD =================
loadDeployments();