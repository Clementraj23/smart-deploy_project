from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    repo_url = data.get("repository", {}).get("clone_url")

    if repo_url:
        print(f"🚀 Auto deploying: {repo_url}")

        subprocess.Popen([
            "curl",
            "-X", "POST",
            "http://localhost:5003/deploy",
            "-H", "Content-Type: application/json",
            "-d", f'{{"repo": "{repo_url}"}}'
        ])

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)