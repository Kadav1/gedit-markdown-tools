# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-27

### Added
- Initial release
- Auto-fix functionality for common markdown issues
  - Header spacing correction (`##Header` → `## Header`)
  - Blank line management around headers, lists, and code blocks
  - List marker normalization (converts `*`, `+` to `-`)
  - Table cell spacing (`|cell|` → `| cell |`)
  - Code block language detection and hints
  - Heading hierarchy validation (prevents level skips)
- mdformat integration for professional formatting
- pymarkdown integration for real-time linting
- Keyboard shortcuts:
  - Ctrl+Alt+F for auto-fix only
  - Ctrl+Alt+M for full pipeline (auto-fix + format + lint)
- Flatpak-aware architecture using `flatpak-spawn --host`
- Visual error highlighting with red underlines
- Configurable settings for all auto-fix features
- Support for Gedit 48+ (Flatpak)

### Technical Details
- Uses Gedit's `WindowActivatable` plugin interface
- GTK 3.0 and Gedit 3.0 API integration
- Regex-based text transformation engine
- Sequential fix pipeline to avoid conflicts
- Temporary file handling for lint operations

[1.0.0]: https://github.com/yourusername/gedit-markdown-tools/releases/tag/v1.0.0
