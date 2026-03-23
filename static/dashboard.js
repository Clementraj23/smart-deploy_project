// ---------------- SOCKET ----------------
const socket = io("http://13.126.46.108:5003", {
    transports: ["websocket"]
});

// DEBUG
socket.on("connect", () => {
    console.log("✅ Connected");
});

socket.on("connect_error", (err) => {
    console.error("❌ Connection failed:", err);
});


// ---------------- CHART ----------------
const ctx = document.getElementById("cpuChart").getContext("2d");

let labels = [];
let dataPoints = [];

const chart = new Chart(ctx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [{
            label: "CPU %",
            data: dataPoints,
            borderWidth: 2,
            tension: 0.3
        }]
    },
    options: {
        animation: false,
        scales: {
            y: {
                min: 0,
                max: 100
            }
        }
    }
});


// ---------------- CPU EVENT ----------------
socket.on("cpu", (value) => {
    console.log("CPU:", value);

    const time = new Date().toLocaleTimeString();

    labels.push(time);
    dataPoints.push(value);

    if (labels.length > 20) {
        labels.shift();
        dataPoints.shift();
    }

    chart.update();

    document.getElementById("cpuText").innerText = `CPU: ${value}%`;
});


// ---------------- ALERT ----------------
socket.on("alert", (msg) => {
    alert(msg);
});


// ---------------- LOGS ----------------
socket.on("logs", (msg) => {
    const box = document.getElementById("logs");
    box.innerText += msg;
    box.scrollTop = box.scrollHeight;
});


// ---------------- DEPLOY ----------------
async function deployRepo() {
    const repo = document.getElementById("repo").value;

    if (!repo) {
        alert("Enter repo URL");
        return;
    }

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
        alert("🚀 Deployed!\n" + data.url);
        loadDeployments();
    }
}


// ---------------- LOAD DEPLOYMENTS ----------------
async function loadDeployments() {
    const res = await fetch("/deployments");
    const data = await res.json();

    const div = document.getElementById("deployments");
    div.innerHTML = "";

    data.forEach(d => {
        const el = document.createElement("div");

        el.innerHTML = `
            <b>${d.name}</b><br>
            <a href="${d.url}" target="_blank">${d.url}</a>
            <hr>
        `;

        div.appendChild(el);
    });
}


// ---------------- AUTO REFRESH ----------------
setInterval(loadDeployments, 5000);
loadDeployments();