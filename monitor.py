import docker
client = docker.from_env()

def get_running_containers():
    containers = client.containers.list()
    data = []

    for c in containers:
        data.append({
            "id": c.id[:6],
            "cpu": 20   # simulated value
        })

    return data