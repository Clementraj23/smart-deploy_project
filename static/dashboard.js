async function deploy() {
    const repo = document.getElementById("repoInput").value;

    const res = await fetch("/deploy", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ repo: repo })
    });

    const data = await res.json();

    if (data.url) {
        window.open(data.url, "_blank");
        loadDeployments();
    } else {
        alert("❌ " + (data.error || "Deploy failed"));
    }
}

async function loadDeployments() {
    const res = await fetch("/deployments");
    const data = await res.json();

    const container = document.getElementById("deployments");
    container.innerHTML = "";

    data.forEach(d => {
        const div = document.createElement("div");
        div.innerHTML = `
            <p>📦 ${d.project}</p>
            <a href="${d.url}" target="_blank">${d.url}</a>
            <pre>${d.logs.slice(-300)}</pre>
            <hr/>
        `;
        container.appendChild(div);
    });
}

setInterval(loadDeployments, 5000);