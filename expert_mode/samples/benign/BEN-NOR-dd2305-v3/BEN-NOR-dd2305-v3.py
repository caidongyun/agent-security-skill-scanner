import shutil
import datetime

def backup_file(source, backup_dir="backups"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source}_{timestamp}.bak"
    dest = f"{backup_dir}/{filename}"
    shutil.copy2(source, dest)
    print(f"Backed up to {dest}")
    return dest

if __name__ == "__main__":
    backup_file("important_data.txt")
