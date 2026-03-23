// ---------------- SOCKET CONNECTION ----------------
const socket = io("http://13.126.46.108:5003", {
    transports: ["websocket"]
});


// ---------------- CPU GRAPH SETUP ----------------
const ctx = document.getElementById("cpuChart").getContext("2d");

let cpuData = [];
let labels = [];

const cpuChart = new Chart(ctx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [{
            label: "CPU Usage %",
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
                min: 0,
                max: 100
            }
        }
    }
});


// ---------------- CPU LIVE UPDATE ----------------
socket.on("cpu", (value) => {
    const now = new Date().toLocaleTimeString();

    labels.push(now);
    cpuData.push(value);

    // keep last 20 points
    if (labels.length > 20) {
        labels.shift();
        cpuData.shift();
    }

    cpuChart.update();

    document.getElementById("cpuText").innerText = `CPU: ${value}%`;
});


// ---------------- ALERT ----------------
socket.on("alert", (msg) => {
    alert(msg);
});


// ---------------- LOG STREAM ----------------
socket.on("logs", (log) => {
    const logBox = document.getElementById("logs");

    logBox.innerText += log;
    logBox.scrollTop = logBox.scrollHeight;
});


// ---------------- DEPLOY FUNCTION ----------------
async function deployRepo() {
    const repo = document.getElementById("repo").value;

    if (!repo) {
        alert("Enter repo URL");
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
            alert("🚀 Deployed successfully!\n" + data.url);
            loadDeployments();
        }

    } catch (err) {
        alert("Deployment failed");
        console.error(err);
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
            const div = document.createElement("div");

            div.innerHTML = `
                <p><b>${d.name}</b></p>
                <a href="${d.url}" target="_blank">${d.url}</a>
                <hr/>
            `;

            container.appendChild(div);
        });

    } catch (err) {
        console.error("Error loading deployments", err);
    }
}


// ---------------- AUTO REFRESH ----------------
setInterval(loadDeployments, 5000);


// ---------------- INITIAL LOAD ----------------
loadDeployments();