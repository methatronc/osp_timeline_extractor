#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:34:25 2025

@author: https://github.com/methatronc
"""

import datetime
import json
import os

import tkinter as tk
import tkinter.filedialog as fd


OPENSHOT = "OpenShot"
KDENLIVE = "Kdenlive"


class TimelineExtractor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("OSP Timeline Extractor")
        self.geometry("600x400")
        self.file_path = None

        self.label = tk.Label(
            self,
            text="Click the button to select a OSP file",
            font=("Arial", 14)
        )
        self.label.pack(pady=10)

        button = tk.Button(
            self,
            text="Select File",
            command=self.on_file_select,
            font=("Arial", 12)
        )
        button.pack(pady=10)

        choice_convert_label = tk.LabelFrame(self, text="Export type")
        choice_convert_label.pack(pady=10)

        self.export_selected = tk.StringVar()
        export_types = (OPENSHOT, KDENLIVE)
        self.export_selected.set(OPENSHOT)
        for export_type in export_types:
            radio = tk.Radiobutton(
                choice_convert_label,
                text=export_type,
                value=export_type,
                variable=self.export_selected,
                command=self.reload
            )
            radio.pack(side="left")

        frame = tk.Frame(self)
        frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_box = tk.Text(
            frame,
            wrap=tk.WORD,
            font=("Courier", 12),
            yscrollcommand=scrollbar.set
        )
        self.text_box.pack(expand=True, fill=tk.BOTH)

        scrollbar.config(command=self.text_box.yview)
        self.text_box.bind("<Control-a>", self.select_all)
        self.text_box.bind("<Control-A>", self.select_all)  # for mac

    def on_file_select(self):
        self.file_path = fd.askopenfilename(
            title="Select your OpenShot project file",
            filetypes=[("OSP files", "*.osp")]
        )
        if self.file_path:
            try:
                self.load_file()
                filename = os.path.basename(self.file_path)
                self.label.config(text=f"Loaded file: {filename}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to load file: {e}")

    def load_file(self):
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, self.compute_content())

    def select_all(self, event: tk.Event) -> str:
        self.text_box.tag_add(tk.SEL, "1.0", tk.END)
        self.text_box.mark_set(tk.INSERT, "1.0")
        self.text_box.see(tk.INSERT)
        return "break"

    def reload(self):
        # only reloads if a file path has been set
        if self.file_path:
            self.load_file()

    def compute_content(self) -> str:
        with open(self.file_path, "r", encoding="utf8") as osp_file:
            content = json.load(osp_file)

        # Kdenlive uses a 0-24 ms range while OpenShot uses a 0-30 range
        max_ms = 30 if self.export_selected.get() == OPENSHOT else 24

        res = ""
        old_title = ""
        for clip in content["clips"]:
            title = clip["title"]
            start = f"{clip["start"]:08.03f}"
            end = f"{clip["end"]:08.03f}"
            out = ""
            for t in start, end:
                hms, ms = t.split(".")
                hms = str(datetime.timedelta(seconds=int(hms)))
                ms = int(ms) * max_ms // 1000
                out += f" {hms}:{ms:02}"
            if old_title != title:
                res += os.linesep
            old_title = title
            res += f"{title:<15} > {out}{os.linesep}"

        return res


if __name__ == "__main__":
    app = TimelineExtractor()
    app.mainloop()
