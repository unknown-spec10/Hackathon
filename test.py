import os

folders = [
    "app/model",
    "app/route",
    "app/schema",
    "app/service",
    "app/utils",
    "database",
    "test",
]

files = {
    "app/model": ["__init__.py", "course.py", "job.py", "org.py", "user.py"],
    "app/service": ["__init__.py"],
    "app/utils": ["__init__.py"],
    "": ["main.py", "README.md", "requirments.txt"],  # root files
}

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    # create empty __init__.py if specified
    if folder in files:
        for f in files[folder]:
            with open(os.path.join(folder, f), "w") as file:
                file.write("")  # create empty file

# create root files
for f in files.get("", []):
    with open(f, "w") as file:
        file.write("")
