# Quick Setup Guide

## 1. Create GitHub Repo

Go to https://github.com/new and create a new repository:

- **Repository name**: `gedit-markdown-tools`
- **Description**: Auto-fix, format, and lint Markdown in Gedit
- **Public/Private**: Your choice
- **Don't** initialize with README, .gitignore, or license (already included)

## 2. Initialize and Push

From this directory:

```bash
# Make init script executable (if not already)
chmod +x init_git.sh

# Run the init script
./init_git.sh

# Add your GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/gedit-markdown-tools.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 3. Done!

Your repository is now live on GitHub with:
- ✓ Comprehensive README with installation, usage, and troubleshooting
- ✓ MIT License
- ✓ Python .gitignore
- ✓ Changelog
- ✓ Plugin files (md_tools.py and md_tools.plugin)

## Optional: Add Topics/Tags on GitHub

After pushing, visit your repo on GitHub and add topics:
- `gedit`
- `gedit-plugin`
- `markdown`
- `markdown-formatter`
- `markdown-linter`
- `flatpak`
- `gtk3`
- `python`

This helps others discover your plugin.
