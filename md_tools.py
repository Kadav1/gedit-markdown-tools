import gi
import subprocess
import re
import os
import tempfile

gi.require_version('Gedit', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import GObject, Gedit, Gio, Gtk, Gdk, Pango, GLib

class MarkdownToolsPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "MarkdownToolsPlugin"
    window = GObject.Property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = {
            "format_on_save": False,
            "auto_fix_on_format": True,
            "fix_headers": True,
            "fix_blank_lines": True,
            "fix_list_markers": True,
            "fix_tables": True,
            "fix_code_blocks": True,
            "fix_heading_hierarchy": True,
        }
        self.handlers = {}

    def do_activate(self):
        self._build_actions()
        self._build_menu()
        self._setup_view_signals()
        
        app = self.window.get_application()
        if not app: app = Gio.Application.get_default()
        if app:
            app.set_accels_for_action("win.mdtools.format_now", ["<Control><Alt>m"])
            app.set_accels_for_action("mdtools.format_now", ["<Control><Alt>m"])
            app.set_accels_for_action("win.mdtools.auto_fix", ["<Control><Alt>f"])
            app.set_accels_for_action("mdtools.auto_fix", ["<Control><Alt>f"])
            print("MarkdownTools: Shortcuts Registered (Ctrl+Alt+M=format, Ctrl+Alt+F=auto-fix)")

    def do_deactivate(self):
        self._remove_menu()
        self._remove_actions()
        self._remove_view_signals()

    def do_update_state(self):
        self._update_ui()
        self._remove_view_signals()
        self._setup_view_signals()

    def _build_actions(self):
        self.action_group = Gio.SimpleActionGroup()
        
        act_fmt = Gio.SimpleAction(name="format_now")
        act_fmt.connect("activate", self.on_manual_format)
        self.action_group.add_action(act_fmt)
        
        act_fix = Gio.SimpleAction(name="auto_fix")
        act_fix.connect("activate", self.on_auto_fix)
        self.action_group.add_action(act_fix)
        
        self.window.insert_action_group("mdtools", self.action_group)

    def _build_menu(self):
        pass

    def _remove_menu(self):
        pass

    def _remove_actions(self):
        self.window.remove_action_group("mdtools")

    def _update_ui(self):
        view = self.window.get_active_view()
        enabled = view is not None
        self.action_group.lookup_action("format_now").set_enabled(enabled)
        self.action_group.lookup_action("auto_fix").set_enabled(enabled)

    def _setup_view_signals(self):
        view = self.window.get_active_view()
        if not view: return
        doc = view.get_buffer()
        if doc in self.handlers: return
        h_id = doc.connect("save", self.on_document_save)
        self.handlers[doc] = h_id
        
        table = doc.get_tag_table()
        if not table.lookup("lint_error"):
            tag = Gtk.TextTag(name="lint_error")
            tag.set_property("underline", Pango.Underline.ERROR)
            table.add(tag)

    def _remove_view_signals(self):
        for doc, h_id in self.handlers.items():
            if doc and GObject.signal_handler_is_connected(doc, h_id):
                doc.disconnect(h_id)
        self.handlers = {}

    def show_debug_popup(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def run_host_command(self, cmd_list, input_text=None):
        full_cmd = ['flatpak-spawn', '--host'] + cmd_list
        print(f"Running: {full_cmd}")
        try:
            return subprocess.run(full_cmd, input=input_text, capture_output=True, text=True)
        except Exception as e:
            self.show_debug_popup("Execution Error", str(e))
            return None

    # ========================================================================
    # AUTO-FIX FUNCTIONS
    # ========================================================================

    def auto_fix_markdown(self, text):
        """Apply all markdown fixes in sequence"""
        original = text
        
        if self.settings["fix_headers"]:
            text = self.fix_header_spacing(text)
        
        if self.settings["fix_blank_lines"]:
            text = self.fix_blank_lines(text)
        
        if self.settings["fix_list_markers"]:
            text = self.fix_list_markers(text)
        
        if self.settings["fix_tables"]:
            text = self.fix_tables(text)
        
        if self.settings["fix_code_blocks"]:
            text = self.fix_code_blocks(text)
        
        if self.settings["fix_heading_hierarchy"]:
            text = self.fix_heading_hierarchy(text)
        
        if text != original:
            print("Auto-fix applied changes")
        
        return text

    def fix_header_spacing(self, text):
        """Fix headers without space after # symbols: ##Header -> ## Header"""
        pattern = r'^(#{1,6})([^\s#])'
        lines = text.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed = re.sub(pattern, r'\1 \2', line)
            fixed_lines.append(fixed)
        
        return '\n'.join(fixed_lines)

    def fix_blank_lines(self, text):
        """Ensure blank lines around headers, lists, code blocks"""
        lines = text.split('\n')
        result = []
        
        for i, line in enumerate(lines):
            prev_line = lines[i-1] if i > 0 else ""
            next_line = lines[i+1] if i < len(lines)-1 else ""
            
            is_header = re.match(r'^#{1,6}\s', line)
            is_list = re.match(r'^[\s]*[-*+]\s', line) or re.match(r'^[\s]*\d+\.\s', line)
            is_code_fence = line.strip().startswith('```')
            
            prev_is_header = re.match(r'^#{1,6}\s', prev_line)
            prev_is_list = re.match(r'^[\s]*[-*+]\s', prev_line) or re.match(r'^[\s]*\d+\.\s', prev_line)
            prev_is_code_fence = prev_line.strip().startswith('```')
            prev_is_empty = prev_line.strip() == ""
            
            if is_header and i > 0 and not prev_is_empty:
                result.append("")
            
            if is_code_fence and i > 0 and not prev_is_empty and not prev_is_code_fence:
                result.append("")
            
            if is_list and i > 0 and not prev_is_list and not prev_is_empty:
                result.append("")
            
            result.append(line)
            
            if is_header and next_line.strip() != "":
                result.append("")
            
            if is_code_fence and next_line.strip() != "" and not next_line.strip().startswith('```'):
                result.append("")
        
        # Clean up multiple consecutive blank lines
        final = []
        blank_count = 0
        for line in result:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 1:
                    final.append(line)
            else:
                blank_count = 0
                final.append(line)
        
        return '\n'.join(final)

    def fix_list_markers(self, text):
        """Normalize list markers to use - consistently"""
        lines = text.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed = re.sub(r'^(\s*)[*+](\s)', r'\1-\2', line)
            fixed_lines.append(fixed)
        
        return '\n'.join(fixed_lines)

    def fix_tables(self, text):
        """Fix basic table formatting issues"""
        lines = text.split('\n')
        result = []
        in_table = False
        table_lines = []
        
        for line in lines:
            if '|' in line and line.strip().startswith('|'):
                in_table = True
                table_lines.append(line)
            else:
                if in_table and table_lines:
                    result.extend(self._fix_table_block(table_lines))
                    table_lines = []
                    in_table = False
                result.append(line)
        
        if table_lines:
            result.extend(self._fix_table_block(table_lines))
        
        return '\n'.join(result)

    def _fix_table_block(self, table_lines):
        """Fix a single table block"""
        if not table_lines:
            return []
        
        fixed = []
        for line in table_lines:
            parts = line.split('|')
            cleaned = []
            for i, part in enumerate(parts):
                if i == 0 and part.strip() == "":
                    cleaned.append("")
                elif i == len(parts) - 1 and part.strip() == "":
                    cleaned.append("")
                else:
                    cleaned.append(f" {part.strip()} ")
            
            fixed_line = '|'.join(cleaned)
            fixed.append(fixed_line)
        
        return fixed

    def fix_code_blocks(self, text):
        """Add language hints to code blocks without them"""
        lines = text.split('\n')
        result = []
        
        for i, line in enumerate(lines):
            if line.strip() == '```' or line.strip() == '~~~':
                next_line = lines[i+1] if i+1 < len(lines) else ""
                
                language = ""
                if 'def ' in next_line or 'import ' in next_line or 'class ' in next_line:
                    language = "python"
                elif 'function ' in next_line or 'const ' in next_line or 'let ' in next_line:
                    language = "javascript"
                elif '<' in next_line and '>' in next_line:
                    language = "html"
                elif '{' in next_line or 'public ' in next_line or 'private ' in next_line:
                    language = "java"
                
                if language:
                    result.append(f"```{language}")
                else:
                    result.append("```text")
            else:
                result.append(line)
        
        return '\n'.join(result)

    def fix_heading_hierarchy(self, text):
        """Fix heading hierarchy skips (e.g., # -> ### becomes # -> ##)"""
        lines = text.split('\n')
        result = []
        last_level = 0
        
        for line in lines:
            match = re.match(r'^(#{1,6})\s', line)
            if match:
                current_level = len(match.group(1))
                
                if last_level > 0 and current_level > last_level + 1:
                    new_level = last_level + 1
                    hashes = '#' * new_level
                    rest = line[current_level:]
                    line = hashes + rest
                    print(f"Fixed heading level skip: {current_level} -> {new_level}")
                
                last_level = len(re.match(r'^(#{1,6})', line).group(1))
            
            result.append(line)
        
        return '\n'.join(result)

    # ========================================================================
    # ACTION HANDLERS
    # ========================================================================

    def on_auto_fix(self, action, param):
        """Manually triggered auto-fix (Ctrl+Alt+F)"""
        view = self.window.get_active_view()
        if not view: return
        doc = view.get_buffer()
        
        start, end = doc.get_bounds()
        text = doc.get_text(start, end, False)
        
        fixed = self.auto_fix_markdown(text)
        
        if fixed != text:
            doc.begin_user_action()
            doc.set_text(fixed)
            doc.end_user_action()
            print("Auto-fix completed")
        else:
            print("No fixes needed")

    def on_manual_format(self, action, param):
        """Manually triggered format+lint (Ctrl+Alt+M)"""
        if self.settings["auto_fix_on_format"]:
            self.on_auto_fix(action, param)
        
        self.format_document()
        self.lint_document()

    def on_document_save(self, doc, *args):
        if self.settings["format_on_save"]:
            if self.settings["auto_fix_on_format"]:
                view = self.window.get_active_view()
                if view and view.get_buffer() == doc:
                    start, end = doc.get_bounds()
                    text = doc.get_text(start, end, False)
                    fixed = self.auto_fix_markdown(text)
                    if fixed != text:
                        doc.begin_user_action()
                        doc.set_text(fixed)
                        doc.end_user_action()
            
            self.format_document(doc)
        self.lint_document(doc)

    def format_document(self, doc=None):
        if not doc:
            view = self.window.get_active_view()
            if not view: return
            doc = view.get_buffer()

        start, end = doc.get_bounds()
        text = doc.get_text(start, end, False)
        
        cmd = ['/home/blndsft/.local/bin/mdformat', '-']
        res = self.run_host_command(cmd, input_text=text)
        
        if res:
            if res.returncode == 0 and res.stdout and res.stdout != text:
                doc.begin_user_action()
                doc.set_text(res.stdout)
                doc.end_user_action()
                print("Formatted successfully")
            elif res.returncode != 0:
                print(f"Format failed: {res.stderr}")
                self.show_debug_popup("Format Failed", f"Error:\n{res.stderr}")

    def lint_document(self, doc=None):
        if not doc:
            view = self.window.get_active_view()
            if not view: return
            doc = view.get_buffer()

        start, end = doc.get_bounds()
        doc.remove_tag_by_name("lint_error", start, end)
        text = doc.get_text(start, end, False)

        home_dir = os.path.expanduser("~")
        temp_path = os.path.join(home_dir, ".gedit_lint_temp.md")
        
        with open(temp_path, "w") as f:
            f.write(text)

        cmd = ['/home/blndsft/.local/bin/pymarkdown', 'scan', temp_path]
        res = self.run_host_command(cmd)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if res:
            if res.stdout or res.stderr:
                self.apply_lint_highlights(doc, res.stdout + res.stderr)
            else:
                print("No lint errors found")

    def apply_lint_highlights(self, doc, output):
        regex = re.compile(r":(\d+):(\d+): (.*)")
        count = 0
        for line in output.splitlines():
            match = regex.search(line)
            if match:
                try:
                    line_num = max(0, int(match.group(1)) - 1)
                    col_num = max(0, int(match.group(2)) - 1)
                    
                    iter_start = doc.get_iter_at_line(line_num)
                    if not iter_start: continue
                    
                    if col_num <= 0:
                        iter_end = iter_start.copy()
                        iter_end.forward_to_line_end()
                    else:
                        iter_start.forward_chars(col_num)
                        iter_end = iter_start.copy()
                        iter_end.forward_word_end()
                    
                    doc.apply_tag_by_name("lint_error", iter_start, iter_end)
                    count += 1
                except ValueError: continue
        if count > 0:
            print(f"Found {count} lint errors")
