# Gedit Markdown Tools

A powerful Gedit plugin for formatting, linting, and auto-fixing Markdown files. Designed specifically for Flatpak installations of Gedit, with automatic handling of AI-generated markdown inconsistencies.

## Features

### 🔧 Auto-Fix Markdown Issues
Automatically detects and fixes common markdown formatting problems:

- **Header spacing**: `##Header` → `## Header`
- **Blank line management**: Proper spacing around headers, lists, and code blocks
- **List marker normalization**: Converts mixed `*`, `+` markers to consistent `-`
- **Table formatting**: Ensures proper cell spacing `|cell|` → `| cell |`
- **Code block language detection**: Adds language hints to bare code fences
- **Heading hierarchy**: Prevents level skips (e.g., `#` → `###` becomes `#` → `##`)

### 📝 Format & Lint
- **mdformat integration**: Professional markdown formatting via `mdformat`
- **pymarkdown linting**: Real-time error highlighting with red underlines
- **Flatpak-aware**: Seamlessly executes host tools from sandboxed Gedit

### ⌨️ Keyboard Shortcuts
- **Ctrl+Alt+F**: Quick auto-fix (corrects formatting issues)
- **Ctrl+Alt+M**: Full pipeline (auto-fix + format + lint)

## Installation

### Prerequisites

1. **Gedit 48+ (Flatpak)**
   ```bash
   flatpak install flathub org.gnome.gedit
   ```

2. **Host tools** (installed on your system, not in Flatpak):
   ```bash
   pip install --user mdformat pymarkdown
   ```

3. **Verify tool paths**:
   ```bash
   which mdformat    # Usually ~/.local/bin/mdformat
   which pymarkdown  # Usually ~/.local/bin/pymarkdown
   ```

### Plugin Installation

1. **Clone or download this repository**:
   ```bash
   git clone https://github.com/yourusername/gedit-markdown-tools.git
   cd gedit-markdown-tools
   ```

2. **Create the Gedit plugins directory** (if it doesn't exist):
   ```bash
   mkdir -p ~/.var/app/org.gnome.gedit/data/gedit/plugins/
   ```

3. **Copy plugin files**:
   ```bash
   cp md_tools.plugin ~/.var/app/org.gnome.gedit/data/gedit/plugins/
   cp md_tools.py ~/.var/app/org.gnome.gedit/data/gedit/plugins/
   ```

4. **Update tool paths in `md_tools.py`**:
   
   Edit lines 347 and 374 to match your tool locations:
   ```python
   # Line 347 (mdformat)
   cmd = ['/home/YOUR_USERNAME/.local/bin/mdformat', '-']
   
   # Line 374 (pymarkdown)
   cmd = ['/home/YOUR_USERNAME/.local/bin/pymarkdown', 'scan', temp_path]
   ```

5. **Enable the plugin**:
   - Launch Gedit: `flatpak run org.gnome.gedit`
   - Go to **Preferences** → **Plugins**
   - Check **"Markdown Tools (Flatpak)"**

6. **Verify installation**:
   - Run Gedit from terminal to see plugin output:
     ```bash
     flatpak run org.gnome.gedit
     ```
   - You should see: `MarkdownTools: Shortcuts Registered (Ctrl+Alt+M=format, Ctrl+Alt+F=auto-fix)`

## Usage

### Quick Start

1. Open or create a `.md` file in Gedit
2. Press **Ctrl+Alt+F** to auto-fix formatting issues
3. Press **Ctrl+Alt+M** to run the full format+lint pipeline

### Workflow for AI-Generated Markdown

Many AI tools generate markdown with inconsistent formatting. Here's the recommended workflow:

1. **Paste AI output** into Gedit
2. **Ctrl+Alt+F** - Fixes headers, lists, tables, code blocks
3. **Ctrl+Alt+M** - Applies mdformat for final polish + shows lint errors
4. **Review red underlines** - Fix any remaining lint issues

### Example Fixes

#### Before:
```markdown
##Broken Header
No spacing around this
* Mixed list
+ markers here
|cell1|cell2|
```

#### After (Ctrl+Alt+F):
```markdown
## Broken Header

No spacing around this

- Mixed list
- markers here

| cell1 | cell2 |
```

## Configuration

Edit the `self.settings` dictionary in `md_tools.py` (around line 19) to customize behavior:

```python
self.settings = {
    "format_on_save": False,          # Auto-format when saving
    "auto_fix_on_format": True,       # Run auto-fix before mdformat
    "fix_headers": True,              # Fix header spacing
    "fix_blank_lines": True,          # Manage blank lines
    "fix_list_markers": True,         # Normalize list markers
    "fix_tables": True,               # Format tables
    "fix_code_blocks": True,          # Add language hints
    "fix_heading_hierarchy": True,    # Fix heading level skips
}
```

**Common customizations:**

- **Enable format-on-save**: Set `"format_on_save": True`
- **Disable code language detection**: Set `"fix_code_blocks": False`
- **Skip blank line insertion**: Set `"fix_blank_lines": False`

Changes take effect after restarting Gedit.

## Troubleshooting

### Plugin doesn't load

**Check plugin location**:
```bash
ls ~/.var/app/org.gnome.gedit/data/gedit/plugins/
# Should show: md_tools.plugin and md_tools.py
```

**Check Gedit version**:
```bash
flatpak run org.gnome.gedit --version
# Requires Gedit 48.1.2 or later
```

**Run from terminal** to see error messages:
```bash
flatpak run org.gnome.gedit
```

### Shortcuts don't work

The plugin registers both `win.mdtools.action` and `mdtools.action` to ensure compatibility. If shortcuts still don't work:

1. Check for conflicts in Gedit's keyboard shortcuts settings
2. Verify the plugin is enabled in Preferences → Plugins
3. Try restarting Gedit completely

### Format/Lint commands fail

**Error: "command not found"**

1. Verify tools are installed on host (not in Flatpak):
   ```bash
   which mdformat
   which pymarkdown
   ```

2. Update paths in `md_tools.py` to match your system

**Error: "Execution Error"**

The plugin uses `flatpak-spawn --host` to access host tools. Ensure:
- You're running the Flatpak version of Gedit (not system version)
- Tools are executable: `chmod +x ~/.local/bin/mdformat`

### Lint highlights don't appear

1. Check that `pymarkdown` is installed and accessible
2. Verify the temp file path is writable:
   ```bash
   touch ~/.gedit_lint_temp.md && rm ~/.gedit_lint_temp.md
   ```
3. Check terminal output for pymarkdown errors

### Code language detection is wrong

The plugin uses simple heuristics (looks for `def`, `import`, `function`, etc.). To improve:

1. Manually specify languages in your markdown
2. Disable auto-detection: `"fix_code_blocks": False`
3. Extend the detection logic in `fix_code_blocks()` (line 267)

## Technical Details

### Architecture

- **Plugin System**: Gedit's `WindowActivatable` interface
- **Sandbox Escape**: `flatpak-spawn --host` for executing host tools
- **Text Processing**: Regex-based transformations with line-by-line parsing
- **Error Highlighting**: GTK `TextTag` with `Pango.Underline.ERROR`

### Auto-Fix Order

Fixes run sequentially to avoid conflicts:

1. Header spacing
2. Blank line insertion
3. List marker normalization
4. Table formatting
5. Code block language detection
6. Heading hierarchy correction

### File Locations

- **Plugin files**: `~/.var/app/org.gnome.gedit/data/gedit/plugins/`
- **Temp lint file**: `~/.gedit_lint_temp.md` (auto-deleted after use)
- **Host tools**: Typically `~/.local/bin/` (must be on host, not in Flatpak)

## Development

### Extending Auto-Fix

To add new fixes, create a method in the `MarkdownToolsPlugin` class:

```python
def fix_custom_issue(self, text):
    """Description of what this fixes"""
    lines = text.split('\n')
    # Your fix logic here
    return '\n'.join(lines)
```

Then add it to the `auto_fix_markdown()` pipeline:

```python
def auto_fix_markdown(self, text):
    # ... existing fixes ...
    
    if self.settings["fix_custom_issue"]:
        text = self.fix_custom_issue(text)
    
    return text
```

### Adding Shortcuts

Register new actions in `_build_actions()` and shortcuts in `do_activate()`:

```python
def _build_actions(self):
    # ... existing actions ...
    
    act_custom = Gio.SimpleAction(name="custom_action")
    act_custom.connect("activate", self.on_custom_action)
    self.action_group.add_action(act_custom)

def do_activate(self):
    # ... existing shortcuts ...
    
    app.set_accels_for_action("win.mdtools.custom_action", ["<Control><Alt>c"])
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Areas for Improvement

- **Settings UI**: GTK dialog for configuration instead of editing Python
- **Language detection**: More sophisticated code language inference
- **Custom lint rules**: User-defined markdown style rules
- **Snippet insertion**: Quick insert common markdown patterns
- **Link validation**: Check for broken internal/external links

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for [Gedit](https://wiki.gnome.org/Apps/Gedit) 48+
- Uses [mdformat](https://github.com/executablebooks/mdformat) for formatting
- Uses [pymarkdown](https://github.com/jackdewinter/pymarkdown) for linting
- Inspired by common issues with AI-generated markdown

## Author

Alex Zewebrand

## Version

1.0.0 - Initial release
