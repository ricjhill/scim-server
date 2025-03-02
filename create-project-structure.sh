# Create the main project directory
mkdir -p scim_server/models scim_server/schemas scim_server/api scim_server/services scim_server/utils

# Create all the files
touch scim_server/main.py
touch scim_server/config.py
touch scim_server/models/user.py
touch scim_server/models/group.py
touch scim_server/models/__init__.py
touch scim_server/schemas/user.py
touch scim_server/schemas/group.py
touch scim_server/schemas/__init__.py
touch scim_server/api/users.py
touch scim_server/api/groups.py
touch scim_server/api/__init__.py
touch scim_server/services/scim.py
touch scim_server/services/__init__.py
touch scim_server/utils/auth.py
touch scim_server/utils/filtering.py
touch scim_server/utils/__init__.py

# Create requirements.txt
touch requirements.txt