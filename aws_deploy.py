import paramiko
import time

def deploy_to_ec2():

    # 🔴 CHANGE THIS
    host = "IP 43.205.130.9"

    username = "ec2-user"
    key_path = "Jammykaizen.pem"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=host,
        username=username,
        key_filename=key_path
    )

    print("Connected to EC2")

    commands = [

        # Update system
        "sudo yum update -y",

        # Install Docker (if not installed)
        "sudo yum install docker -y",

        # Start Docker
        "sudo service docker start",

        # Enable Docker on boot
        "sudo systemctl enable docker",

        # Give permission
        "sudo usermod -a -G docker ec2-user",

        # Remove old containers safely
        "sudo docker rm -f $(sudo docker ps -aq) || true",

        # Run SmartDeploy Cloud App
        """sudo docker run -d -p 80:5000 python:3.9-slim \
bash -c "pip install flask && \
echo 'from flask import Flask; app=Flask(__name__); \
@app.route(\"/\") \
def home(): return \"SmartDeploy Cloud App Running\"; \
app.run(host=\"0.0.0.0\",port=5000)' > app.py && python app.py"
"""
    ]

    for cmd in commands:
        print(f"Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)

        # wait for command to complete
        stdout.channel.recv_exit_status()

        # optional logs
        print(stdout.read().decode())
        print(stderr.read().decode())

        time.sleep(2)

    ssh.close()

    print("Deployment complete")

    return {
        "ip": host
    }