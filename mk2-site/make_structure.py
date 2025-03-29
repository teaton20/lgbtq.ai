import os

# Define the directories to create
directories = [
    "src/components",
    "src/layouts",
    "src/pages",
    "src/styles",
    "src/state",
    "src/utils"
]

# Create each directory (including intermediate directories)
for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Define the files for each directory
files = {
    "src/components": [
        "AnonymousSupportForm.jsx",
        "ChatInput.jsx",
        "ChatWindow.jsx",
        "DiscoverCard.jsx",
        "DiscoverFeed.jsx",
        "DiscoverFilters.jsx",
        "FollowUpSuggestions.jsx",
        "HeroSearch.jsx",
        "InlineCitation.jsx",
        "QuickExitButton.jsx",
        "Sidebar.jsx",
        "ThreadControls.jsx",
        "ThreadList.jsx",
        "TopNavBar.jsx",
    ],
    "src/layouts": [
        "DesktopLayout.jsx",
        "MainLayout.jsx",
        "MobileLayout.jsx",
    ],
    "src/pages": [
        "Discover.jsx",
        "Home.jsx",
        "Support.jsx",
    ],
    "src/styles": [
        "colors.css",
        "layout.css",
        "typography.css",
    ],
    "src/state": [
        "GlobalStateContext.jsx",
        "reducer.js",
    ],
    "src/utils": [
        "api.js",
        "helpers.js",
        "storage.js",
    ],
    "src": [  # Files directly in the 'src' folder
        "App.jsx",
        "index.js",
    ]
}

# Create each file by opening it in write mode (creates an empty file)
for folder, file_list in files.items():
    for file_name in file_list:
        file_path = os.path.join(folder, file_name)
        with open(file_path, "w") as f:
            # Optionally, you can write default content here
            f.write("")
            
print("Folder tree created successfully!")
