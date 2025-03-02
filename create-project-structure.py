import os

structure = {
    "scim_server": [
        "main.py", "config.py",
        {"models": ["user.py", "group.py"]},
        {"schemas": ["user.py", "group.py"]},
        {"api": ["users.py", "groups.py"]},
        {"services": ["scim.py"]},
        {"utils": ["auth.py", "filtering.py"]}
    ]
}

def create_structure(base, items):
    for item in items:
        if isinstance(item, str):
            open(os.path.join(base, item), 'w').close()
        elif isinstance(item, dict):
            for folder, files in item.items():
                folder_path = os.path.join(base, folder)
                os.makedirs(folder_path, exist_ok=True)
                create_structure(folder_path, files)

create_structure(".", structure)
