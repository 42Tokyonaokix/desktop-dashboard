"""Dashboard settings window using tkinter."""

import logging
import os
import tkinter as tk
from tkinter import ttk, filedialog
from typing import Callable, Optional

import yaml

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings dashboard for configuring wallpaper display."""

    def __init__(
        self,
        config: dict,
        on_update_callback: Callable,
        on_save_callback: Callable,
    ) -> None:
        self._config = config
        self._on_update = on_update_callback
        self._on_save = on_save_callback
        self._root: Optional[tk.Tk] = None
        self._task_editor_window: Optional[tk.Toplevel] = None

    def get_config(self) -> dict:
        return self._config

    def set_section_order(self, order: list) -> None:
        self._config["dashboard"]["sections"] = order

    def toggle_section(self, section: str, enabled: bool) -> None:
        sections = self._config["dashboard"]["sections"]
        if enabled and section not in sections:
            sections.append(section)
        elif not enabled and section in sections:
            sections.remove(section)

    def _build_ui(self) -> None:
        """Build the settings UI with tabs."""
        notebook = ttk.Notebook(self._root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Display Settings
        display_frame = ttk.Frame(notebook)
        notebook.add(display_frame, text="表示設定")
        self._build_display_tab(display_frame)

        # Tab 2: Vault Settings
        vault_frame = ttk.Frame(notebook)
        notebook.add(vault_frame, text="Vault設定")
        self._build_vault_tab(vault_frame)

        # Tab 3: Task Editor
        task_frame = ttk.Frame(notebook)
        notebook.add(task_frame, text="タスク管理")
        self._build_task_tab(task_frame)

        # Bottom buttons
        btn_frame = ttk.Frame(self._root)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(btn_frame, text="即時更新", command=self._on_refresh).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="保存", command=self._on_save_click).pack(
            side="right", padx=5
        )

    def _build_display_tab(self, parent: ttk.Frame) -> None:
        """Build display settings tab: sections, opacity, font, weights."""
        dash = self._config["dashboard"]

        # Section toggles
        lf = ttk.LabelFrame(parent, text="セクション表示")
        lf.pack(fill="x", padx=10, pady=5)

        self._section_vars = {}
        for section in ["weather", "tasks", "motivation"]:
            var = tk.BooleanVar(value=section in dash["sections"])
            self._section_vars[section] = var
            ttk.Checkbutton(lf, text=section, variable=var).pack(anchor="w", padx=10)

        # Section order
        lf2 = ttk.LabelFrame(parent, text="セクション順序 (カンマ区切り)")
        lf2.pack(fill="x", padx=10, pady=5)
        self._order_var = tk.StringVar(value=", ".join(dash["sections"]))
        ttk.Entry(lf2, textvariable=self._order_var, width=40).pack(padx=10, pady=5)

        # Weights
        lf3 = ttk.LabelFrame(parent, text="セクション比率 (カンマ区切り)")
        lf3.pack(fill="x", padx=10, pady=5)
        self._weights_var = tk.StringVar(
            value=", ".join(str(w) for w in dash["section_weights"])
        )
        ttk.Entry(lf3, textvariable=self._weights_var, width=40).pack(padx=10, pady=5)

        # Opacity slider
        lf4 = ttk.LabelFrame(parent, text="カード透明度")
        lf4.pack(fill="x", padx=10, pady=5)
        self._opacity_var = tk.DoubleVar(value=dash["card_opacity"])
        tk.Scale(
            lf4, from_=0.0, to=1.0, resolution=0.05,
            orient="horizontal", variable=self._opacity_var,
        ).pack(fill="x", padx=10)

        # Font size
        lf5 = ttk.LabelFrame(parent, text="フォントサイズ")
        lf5.pack(fill="x", padx=10, pady=5)
        self._fontsize_var = tk.IntVar(value=dash["font_size"])
        tk.Scale(
            lf5, from_=12, to=72, orient="horizontal", variable=self._fontsize_var,
        ).pack(fill="x", padx=10)

    def _build_vault_tab(self, parent: ttk.Frame) -> None:
        """Build vault settings tab: directories, task count."""
        obs = self._config["obsidian"]

        # Vault directory
        lf = ttk.LabelFrame(parent, text="Vault ディレクトリ")
        lf.pack(fill="x", padx=10, pady=5)
        self._vault_dir_var = tk.StringVar(value=obs["vault_dir"])
        row = ttk.Frame(lf)
        row.pack(fill="x", padx=10, pady=5)
        ttk.Entry(row, textvariable=self._vault_dir_var, width=35).pack(side="left")
        ttk.Button(row, text="参照", command=self._browse_vault_dir).pack(side="left", padx=5)

        # Motivation file
        lf2 = ttk.LabelFrame(parent, text="励ましコメントファイル")
        lf2.pack(fill="x", padx=10, pady=5)
        self._motivation_var = tk.StringVar(value=obs["motivation_file"])
        row2 = ttk.Frame(lf2)
        row2.pack(fill="x", padx=10, pady=5)
        ttk.Entry(row2, textvariable=self._motivation_var, width=35).pack(side="left")
        ttk.Button(row2, text="参照", command=self._browse_motivation_file).pack(
            side="left", padx=5
        )

        # Task max items
        lf3 = ttk.LabelFrame(parent, text="タスク表示件数")
        lf3.pack(fill="x", padx=10, pady=5)
        self._max_tasks_var = tk.IntVar(value=obs["tasks"]["max_items"])
        tk.Scale(
            lf3, from_=1, to=20, orient="horizontal", variable=self._max_tasks_var,
        ).pack(fill="x", padx=10)

    def _build_task_tab(self, parent: ttk.Frame) -> None:
        """Build task editor tab: file list + text editor."""
        # File list (left side)
        list_frame = ttk.Frame(parent)
        list_frame.pack(side="left", fill="y", padx=5, pady=5)

        ttk.Label(list_frame, text="タスクファイル:").pack(anchor="w")
        self._task_listbox = tk.Listbox(list_frame, width=30, height=15)
        self._task_listbox.pack(fill="y", expand=True)
        self._task_listbox.bind("<<ListboxSelect>>", self._on_task_select)

        ttk.Button(list_frame, text="更新", command=self._refresh_task_list).pack(
            fill="x", pady=5
        )

        # Editor (right side)
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        ttk.Label(editor_frame, text="内容:").pack(anchor="w")
        self._task_editor = tk.Text(editor_frame, wrap="word", width=50, height=15)
        self._task_editor.pack(fill="both", expand=True)

        ttk.Button(editor_frame, text="保存", command=self._save_task_file).pack(
            anchor="e", pady=5
        )

        self._task_files: list = []

    def _browse_vault_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self._vault_dir_var.get())
        if path:
            self._vault_dir_var.set(path)

    def _browse_motivation_file(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=os.path.dirname(self._motivation_var.get()),
            filetypes=[("Markdown", "*.md"), ("All", "*.*")],
        )
        if path:
            self._motivation_var.set(path)

    def _refresh_task_list(self) -> None:
        """Scan vault tasks directory and populate listbox."""
        self._task_listbox.delete(0, tk.END)
        self._task_files = []

        vault_dir = self._vault_dir_var.get()
        tasks_dir = os.path.join(vault_dir, "tasks")
        if not os.path.isdir(tasks_dir):
            return

        from pathlib import Path
        for md_file in sorted(Path(tasks_dir).rglob("*.md")):
            self._task_files.append(str(md_file))
            display = str(md_file.relative_to(tasks_dir))
            self._task_listbox.insert(tk.END, display)

    def _on_task_select(self, event) -> None:
        """Load selected task file into editor."""
        selection = self._task_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        file_path = self._task_files[idx]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self._task_editor.delete("1.0", tk.END)
            self._task_editor.insert("1.0", content)
        except Exception:
            logger.exception("Failed to read task file: %s", file_path)

    def _save_task_file(self) -> None:
        """Save editor content back to the selected task file."""
        selection = self._task_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        file_path = self._task_files[idx]
        content = self._task_editor.get("1.0", tk.END)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info("Saved task file: %s", file_path)
        except Exception:
            logger.exception("Failed to save task file: %s", file_path)

    def _apply_display_settings(self) -> None:
        """Read UI values back into config."""
        dash = self._config["dashboard"]

        # Sections
        active = [s for s, v in self._section_vars.items() if v.get()]
        # Respect order from order field
        order_str = self._order_var.get()
        ordered = [s.strip() for s in order_str.split(",") if s.strip()]
        dash["sections"] = [s for s in ordered if s in active]

        # Weights
        weight_str = self._weights_var.get()
        try:
            dash["section_weights"] = [int(w.strip()) for w in weight_str.split(",")]
        except ValueError:
            pass

        dash["card_opacity"] = self._opacity_var.get()
        dash["font_size"] = self._fontsize_var.get()

        # Vault settings
        obs = self._config["obsidian"]
        obs["vault_dir"] = self._vault_dir_var.get()
        obs["motivation_file"] = self._motivation_var.get()
        obs["tasks"]["max_items"] = self._max_tasks_var.get()

    def _on_refresh(self) -> None:
        """Immediate wallpaper update."""
        self._apply_display_settings()
        self._on_update()

    def _on_save_click(self) -> None:
        """Save config and trigger update."""
        self._apply_display_settings()
        self._on_save(self._config)
        self._on_update()

    def _show_window(self) -> None:
        if self._root:
            self._root.deiconify()
            self._root.lift()
            self._root.focus_force()

    def _hide_window(self) -> None:
        if self._root:
            self._root.withdraw()

    def run(self, on_tick: Callable, weather_interval_ms: int, obsidian_interval_ms: int) -> None:
        """Start the settings window with tkinter mainloop."""
        self._root = tk.Tk()
        self._root.title("Desktop Dashboard 設定")
        self._root.geometry("700x500")
        self._root.resizable(True, True)

        self._root.protocol("WM_DELETE_WINDOW", self._hide_window)
        self._root.createcommand("::tk::mac::ReopenApplication", self._show_window)

        self._build_ui()
        self._refresh_task_list()

        # Start hidden
        self._root.withdraw()

        # Schedule ticks via tkinter.after()
        def weather_tick():
            on_tick("weather")
            self._root.after(weather_interval_ms, weather_tick)

        def obsidian_tick():
            on_tick("obsidian")
            self._root.after(obsidian_interval_ms, obsidian_tick)

        # Initial tick after event loop starts
        self._root.after(100, lambda: on_tick("all"))
        self._root.after(weather_interval_ms, weather_tick)
        self._root.after(obsidian_interval_ms, obsidian_tick)

        self._root.mainloop()
