import docker

client = docker.from_env()

def deploy_app(containers):
    container = client.containers.run(
        "nginx",              # stable image
        detach=True,
        restart_policy={"Name": "always"}
    )
    return container.id
