const socket = io();

// DEPLOY
function deploy() {
    const project = document.getElementById("project").value;

    fetch("/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `project=${project}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.url) {
            window.open(data.url, "_blank");
        }
        loadDeployments();
    });
}

// LOAD DEPLOYMENTS
function loadDeployments() {
    fetch("/deployments")
    .then(res => res.json())
    .then(data => {
        let html = "";
        data.forEach(d => {
            html += `
            <div>
                ${d.project}
                <button onclick="start('${d.id}')">Start</button>
                <button onclick="stop('${d.id}')">Stop</button>
                <button onclick="del('${d.id}')">Delete</button>
                <a href="http://13.126.46.108:${d.port}" target="_blank">Open</a>
            </div>`;
        });
        document.getElementById("deployments").innerHTML = html;
    });
}

function start(id){ fetch(`/start/${id}`); }
function stop(id){ fetch(`/stop/${id}`); }
function del(id){ fetch(`/delete/${id}`); }

// LOGS
socket.on("logs", data => {
    document.getElementById("logs").textContent += data;
});

// ALERTS
socket.on("alert", data => {
    document.getElementById("alerts").innerHTML += `<p>${data}</p>`;
});

// CPU GRAPH
const ctx = document.getElementById("cpuChart").getContext("2d");

const chart = new Chart(ctx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "CPU %",
            data: []
        }]
    }
});

socket.on("cpu", cpu => {
    chart.data.labels.push("");
    chart.data.datasets[0].data.push(cpu);
    chart.update();
});

// FETCH CPU
setInterval(() => {
    fetch("/cpu");
}, 2000);

loadDeployments();