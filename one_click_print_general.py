from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# --- User configuration -------------------------------------------------------

# Default folder when no path is passed and --pick is not used.
PRINT_FOLDER = Path(r"C:\path\to\your\print-queue-folder")

# None = Windows default printer; otherwise exact queue name from Windows.
PRINTER_NAME: str | None = None

# If True, include only PDFs. If False, include PDFs, images, and office/text types.
PRINT_ONLY_PDF = False

# Force PDF jobs to print single-sided (simplex) when SumatraPDF is available.
FORCE_PDF_SIMPLEX = True

# Common SumatraPDF installs.
SUMATRA_CANDIDATES = [
    Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    / "SumatraPDF"
    / "SumatraPDF.exe",
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    / "SumatraPDF"
    / "SumatraPDF.exe",
    Path.home() / "AppData" / "Local" / "SumatraPDF" / "SumatraPDF.exe",
]

# Image types printed via Pillow + pywin32.
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp"}

# Other types sent through ShellExecute "print".
EXTRA_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}

# Wait after ShellExecute so associated apps can receive the print command.
SHELLEXECUTE_PRINT_DELAY_SEC = 3.0

# ------------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print all supported files from a folder (non-recursive)."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        metavar="FOLDER",
        help="Folder to print (optional). Overrides env and PRINT_FOLDER.",
    )
    parser.add_argument(
        "--pick",
        action="store_true",
        help="Open a folder picker dialog (ignored if FOLDER is given).",
    )
    return parser.parse_args(argv)


def pick_folder_dialog() -> Path | None:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    chosen = filedialog.askdirectory(title="Choose folder to print")
    root.destroy()
    if not chosen:
        return None
    return Path(chosen).resolve()


def resolve_print_folder(cli_folder: str | None, use_pick: bool) -> Path:
    if cli_folder:
        raw = cli_folder.strip().strip('"')
        folder = Path(raw).expanduser().resolve()
    elif os.environ.get("ONE_CLICK_PRINT_FOLDER"):
        raw = os.environ["ONE_CLICK_PRINT_FOLDER"].strip().strip('"')
        folder = Path(raw).expanduser().resolve()
    elif use_pick:
        picked = pick_folder_dialog()
        if picked is None:
            raise FileNotFoundError("No folder selected in the dialog.")
        folder = picked
    else:
        folder = Path(PRINT_FOLDER).expanduser().resolve()

    if not folder.is_dir():
        raise FileNotFoundError(f"Not a directory: {folder}")
    return folder


def resolve_printer_name() -> str:
    if PRINTER_NAME:
        return PRINTER_NAME
    import win32print

    return win32print.GetDefaultPrinter()


def collect_files(folder: Path) -> list[Path]:
    if PRINT_ONLY_PDF:
        exts = {".pdf"}
    else:
        exts = set(IMAGE_EXTENSIONS)
        exts.update(EXTRA_EXTENSIONS)

    files: list[Path] = []
    for p in sorted(folder.iterdir(), key=lambda x: x.name.lower()):
        if p.is_file() and p.suffix.lower() in exts:
            files.append(p)
    return files


def find_sumatra() -> Path | None:
    for candidate in SUMATRA_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def print_image_devmode(image_path: Path, printer_name: str) -> None:
    import win32gui
    import win32ui
    from PIL import Image, ImageWin

    hdc = win32gui.CreateDC(None, printer_name, None)
    try:
        dc = win32ui.CreateDCFromHandle(hdc)
        try:
            printable_w = dc.GetDeviceCaps(8)  # HORZRES
            printable_h = dc.GetDeviceCaps(10)  # VERTRES

            img = Image.open(image_path)
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            scale = min(printable_w / img.size[0], printable_h / img.size[1])
            new_w = max(1, int(img.size[0] * scale))
            new_h = max(1, int(img.size[1] * scale))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            dc.StartDoc(image_path.name)
            try:
                dc.StartPage()
                dib = ImageWin.Dib(img)
                dib.draw(dc.GetHandleOutput(), (0, 0, new_w, new_h))
                dc.EndPage()
            finally:
                dc.EndDoc()
        finally:
            dc.DeleteDC()
    finally:
        win32gui.DeleteDC(hdc)


def print_via_shell_execute(path: Path) -> None:
    import win32api
    import win32con

    win32api.ShellExecute(0, "print", str(path.resolve()), None, ".", win32con.SW_HIDE)


def print_pdf_sumatra_simplex(path: Path, printer_name: str, sumatra: Path) -> None:
    result = subprocess.run(
        [
            str(sumatra),
            "-silent",
            "-print-to",
            printer_name,
            "-print-settings",
            "simplex",
            str(path.resolve()),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(
            f"SumatraPDF failed ({result.returncode}) for {path.name}: {err or 'no output'}"
        )


def print_pdf_with_windows(path: Path, printer_name: str, sumatra: Path | None) -> None:
    if FORCE_PDF_SIMPLEX and sumatra:
        print_pdf_sumatra_simplex(path, printer_name, sumatra)
        return

    # Uses PDFtoPrinter if available for direct queue printing.
    pdftoprinter = (
        Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        / "PDFtoPrinter"
        / "PDFtoPrinter.exe"
    )
    if pdftoprinter.is_file():
        result = subprocess.run(
            [str(pdftoprinter), str(path.resolve()), printer_name],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return

    print_via_shell_execute(path)
    time.sleep(SHELLEXECUTE_PRINT_DELAY_SEC)


def main() -> int:
    if sys.platform != "win32":
        print("This script is intended for Windows.", file=sys.stderr)
        return 1

    args = parse_args()
    try:
        print_folder = resolve_print_folder(args.folder, args.pick)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    try:
        printer = resolve_printer_name()
    except Exception as e:  # pragma: no cover - Windows specific path
        print(f"Could not resolve printer: {e}", file=sys.stderr)
        return 1

    files = collect_files(print_folder)
    if not files:
        print(f"No matching files in {print_folder}")
        return 0

    sumatra = find_sumatra()

    print(f"Printer: {printer}")
    print(f"Folder:  {print_folder}")
    print(f"Files:   {len(files)}")
    if FORCE_PDF_SIMPLEX:
        if sumatra:
            print(f"PDF mode: simplex via Sumatra ({sumatra})")
        else:
            print(
                "PDF mode: simplex requested, but SumatraPDF not found; "
                "falling back to Windows app defaults.",
                file=sys.stderr,
            )
    print()

    errors: list[str] = []
    for path in files:
        ext = path.suffix.lower()
        try:
            if ext == ".pdf":
                print_pdf_with_windows(path, printer, sumatra)
                print(f"OK (pdf)    {path.name}")
            elif ext in IMAGE_EXTENSIONS:
                print_image_devmode(path, printer)
                print(f"OK (image)  {path.name}")
            else:
                print_via_shell_execute(path)
                print(f"OK (shell)  {path.name}")
                time.sleep(SHELLEXECUTE_PRINT_DELAY_SEC)
        except Exception as e:
            errors.append(f"{path.name}: {e}")
            print(f"FAIL        {path.name}: {e}", file=sys.stderr)

    if errors:
        print(f"\nFinished with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
