from flask import Flask, request, jsonify, render_template
import subprocess
import os
import random

app = Flask(__name__)

deployments = []

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")


# ---------------- GET DEPLOYMENTS ----------------
@app.route("/deployments")
def get_deployments():
    return jsonify(deployments)


# ---------------- DEPLOY FUNCTION ----------------
@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.json
    repo_url = data.get("repo")

    if not repo_url:
        return jsonify({"error": "No repo URL provided"}), 400

    # Extract repo name
    name = repo_url.split("/")[-1].replace(".git", "")
    port = random.randint(5005, 5999)

    try:
        # Remove old folder if exists
        if os.path.exists(name):
            subprocess.run(["rm", "-rf", name])

        # Clone repo
        subprocess.run(["git", "clone", repo_url], check=True)

        dockerfile_path = f"{name}/Dockerfile"

        # 🔥 AUTO CREATE DOCKERFILE IF NOT PRESENT
        if not os.path.exists(dockerfile_path):
            print("⚡ No Dockerfile found → creating one")

            with open(dockerfile_path, "w") as f:
                f.write("""FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install flask
CMD ["python", "app.py"]
""")

        # Build Docker image
        subprocess.run([
            "docker", "build", "-t", name, name
        ], check=True)

        container_name = f"{name}_{port}"

        # Run container
        subprocess.run([
            "docker", "run", "-d",
            "-p", f"{port}:5000",
            "--name", container_name,
            name
        ], check=True)

        url = f"http://13.126.46.108:{port}"

        deployments.append({
            "project": name,
            "url": url,
            "logs": "🚀 Deployment successful"
        })

        return jsonify({
            "message": "Deployed successfully",
            "url": url
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": f"Deployment failed: {str(e)}"
        })


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
