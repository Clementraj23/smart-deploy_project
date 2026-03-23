const API_BASE = ""; // same origin

// ---------------- DEPLOY ----------------
async function deployRepo() {
    const repoInput = document.getElementById("repo");
    const repo = repoInput.value.trim();

    if (!repo) {
        alert("❌ Please enter a GitHub repo URL");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/deploy`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ repo })
        });

        const data = await res.json();

        if (data.url) {
            alert("🚀 Deployed successfully!\n" + data.url);
            repoInput.value = "";
            loadDeployments(); // refresh list
        } else {
            alert("❌ " + (data.error || "Deployment failed"));
        }

    } catch (err) {
        alert("❌ Server error: " + err.message);
    }
}


// ---------------- LOAD DEPLOYMENTS ----------------
async function loadDeployments() {
    try {
        const res = await fetch(`${API_BASE}/deployments`);
        const data = await res.json();

        const container = document.getElementById("deployments");
        container.innerHTML = "";

        if (data.length === 0) {
            container.innerHTML = "<p>No deployments yet 🚫</p>";
            return;
        }

        data.forEach(d => {
            const div = document.createElement("div");
            div.className = "deployment-card";

            div.innerHTML = `
                <h3>📦 ${d.project}</h3>
                <p>
                    🔗 <a href="${d.url}" target="_blank">${d.url}</a>
                </p>
                <p style="color: lightgreen;">${d.logs}</p>
                <hr/>
            `;

            container.appendChild(div);
        });

    } catch (err) {
        console.error("Error loading deployments:", err);
    }
}


// ---------------- AUTO REFRESH ----------------
setInterval(loadDeployments, 5000);


// ---------------- INITIAL LOAD ----------------
window.onload = () => {
    loadDeployments();
};