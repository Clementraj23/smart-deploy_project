const socket = io();

// ---------------- CPU LIVE ----------------
socket.on("cpu", (data) => {
    document.getElementById("cpu").innerText = "CPU: " + data.cpu + "%";
});

// ---------------- ALERT ----------------
socket.on("alert", (msg) => {
    alert(msg);
});

// ---------------- LOAD DEPLOYMENTS ----------------
async function loadDeployments() {
    const res = await fetch("/deployments");
    const data = await res.json();

    const container = document.getElementById("deployments");
    container.innerHTML = "";

    data.forEach(d => {
        const div = document.createElement("div");

        div.innerHTML = `
            <p><b>${d.name}</b></p>
            <a href="${d.url}" target="_blank">${d.url}</a>
            <pre>${d.logs}</pre>
            <hr/>
        `;

        container.appendChild(div);
    });
}

// ---------------- DEPLOY ----------------
async function deployRepo() {
    const repo = document.getElementById("repo").value;

    if (!repo) {
        alert("Enter GitHub repo URL");
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

    if (data.url) {
        alert("🚀 Deployed: " + data.url);
        loadDeployments();
    } else {
        alert("❌ " + data.error);
    }
}

// auto refresh
setInterval(loadDeployments, 5000);