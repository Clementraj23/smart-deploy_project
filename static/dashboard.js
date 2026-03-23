const socket = io();

// ---------------- DEPLOY ----------------
async function deploy() {
    const repo = document.getElementById("repo").value;

    const res = await fetch("/deploy", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ repo })
    });

    const data = await res.json();

    if (data.url) {
        alert("🚀 Deployed: " + data.url);
        loadDeployments();
    } else {
        alert(data.error);
    }
}

// ---------------- DEPLOYMENTS ----------------
async function loadDeployments() {
    const res = await fetch("/deployments");
    const data = await res.json();

    const div = document.getElementById("deployments");
    div.innerHTML = "";

    data.forEach(d => {
        div.innerHTML += `
            <p>
                📦 ${d.name} →
                <a href="${d.url}" target="_blank">${d.url}</a>
            </p>
        `;
    });
}

// ---------------- CPU GRAPH ----------------
const ctx = document.getElementById("cpuChart").getContext("2d");

const cpuData = {
    labels: [],
    datasets: [{
        label: "CPU %",
        data: [],
        borderWidth: 2,
        tension: 0.3
    }]
};

const cpuChart = new Chart(ctx, {
    type: "line",
    data: cpuData,
    options: {
        responsive: true,
        scales: {
            y: {
                min: 0,
                max: 100
            }
        }
    }
});

// ---------------- SOCKET EVENTS ----------------

// CPU update → graph
socket.on("cpu", (cpu) => {

    const time = new Date().toLocaleTimeString();

    cpuData.labels.push(time);
    cpuData.datasets[0].data.push(cpu);

    // keep last 20 points
    if (cpuData.labels.length > 20) {
        cpuData.labels.shift();
        cpuData.datasets[0].data.shift();
    }

    cpuChart.update();
});

// ALERT
socket.on("alert", (msg) => {
    const alertBox = document.getElementById("alerts");
    alertBox.innerHTML += `<p>${msg}</p>`;
});

// LOGS
socket.on("logs", (log) => {
    const logBox = document.getElementById("logs");
    logBox.innerText += log;
    logBox.scrollTop = logBox.scrollHeight;
});

// auto refresh
setInterval(loadDeployments, 5000);