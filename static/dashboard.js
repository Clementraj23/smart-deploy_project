const socket = io();

// ---------------- DEPLOY ----------------
async function deployRepo() {
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
    } else {
        alert("❌ " + data.error);
    }
}


// ---------------- REALTIME EVENTS ----------------

// CPU
socket.on("cpu", (data) => {
    document.getElementById("cpu").innerText = "CPU: " + data + "%";
});

// ALERT
socket.on("alert", (msg) => {
    alert(msg);
});

// NEW DEPLOY
socket.on("new_deploy", (d) => {
    addDeployment(d);
});

// LOGS
socket.on("logs", (data) => {
    document.getElementById("logs").innerText = data.logs;
});


// ---------------- UI ----------------
function addDeployment(d) {
    const container = document.getElementById("deployments");

    const div = document.createElement("div");
    div.className = "card";

    div.innerHTML = `
        <h3>${d.project}</h3>
        <a href="${d.url}" target="_blank">${d.url}</a>
    `;

    container.appendChild(div);
}