import os


# 🔍 Define Paths (Use Absolute Paths)
BASE_DIR = os.path.abspath("./")  # Adjust if necessary
ASSETS_FOLDER = os.path.join(BASE_DIR, "public/assets")
PROJECT_FOLDER = os.path.join(BASE_DIR, "src")  # Adjust for src/ if needed

# 🔍 File Extensions to Scan
EXTENSIONS_TO_SEARCH = (".tsx", ".ts", ".jsx", ".js", ".mdx", ".html", ".css", ".scss", ".json", ".yml", ".yaml")

# 🛠️ Get All Asset Files
def get_asset_files():
    asset_files = []
    for root, _, files in os.walk(ASSETS_FOLDER):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), ASSETS_FOLDER)
            web_path = f"/assets/{relative_path.replace('\\', '/')}"  # Normalize for web usage
            asset_files.append(web_path)
    return asset_files

# 🛠️ Get All Project Files
def get_project_files():
    project_files = []
    for root, _, files in os.walk(PROJECT_FOLDER):
        for file in files:
            if file.endswith(EXTENSIONS_TO_SEARCH):
                project_files.append(os.path.join(root, file))
    return project_files

# 🔍 Load All Project Files (for faster search)
def load_project_files(project_files):
    project_data = []
    for file in project_files:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            project_data.append(f.read())
    return "\n".join(project_data)  # Join all file contents into a single string

# 🔥 Find Unused Assets
def find_unused_assets():
    print("\n🔍 Scanning for unused assets...")
    # Ignore .DS_Store files
    asset_files = [asset for asset in get_asset_files() if not asset.endswith(".DS_Store")]
  
    project_files = get_project_files()

    # ✅ Load all project files into memory (Optimized for Performance)
    project_data = load_project_files(project_files)

    unused_assets = [asset for asset in asset_files if asset not in project_data]

    print("\n📂 Unused Assets:")
    if unused_assets:
        for asset in unused_assets:
            print(f"❌ {asset}")
    else:
        print("✅ No unused assets found!")

if __name__ == "__main__":
    find_unused_assets()