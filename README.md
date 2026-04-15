# ONE-CLICK-PRINT-GENERAL

Windows one-click printing utility for File Explorer workflows.

This project prints all supported files from one folder (non-recursive), either:
- by passing a folder path,
- by choosing a folder from a picker dialog,
- or by setting a default folder in the script.

## Included files

- `one_click_print_general.py` - main script.
- `Run One-Click Print.bat` - launcher you can double-click, run from cmd, or drag/drop a folder onto.
- `requirements.txt` - Python dependencies.

## Setup

1. Install Python 3.11+ (Windows).
2. In this project folder:
   - `python -m pip install -r requirements.txt`
3. Open `one_click_print_general.py` and set:
   - `PRINT_FOLDER` to your usual folder.
   - `PRINTER_NAME` to your exact Windows printer queue name, or keep `None` for default printer.

## Usage

### Option A: Double-click the batch file

- `Run One-Click Print.bat`

### Option B: Drag and drop a folder onto the batch file

- Explorer will pass that folder path automatically.

### Option C: Run from terminal

- `python one_click_print_general.py "D:\Jobs\Today"`
- `python one_click_print_general.py --pick`

### Optional environment variable

- PowerShell (current session):
  - `$env:ONE_CLICK_PRINT_FOLDER = "D:\Jobs\Today"`
  - `python .\one_click_print_general.py`

## Notes

- PDF and non-image documents use Windows `ShellExecute("print")` unless `PDFtoPrinter.exe` is installed.
- If available at `C:\Program Files\PDFtoPrinter\PDFtoPrinter.exe`, PDFs are sent directly to your selected queue first.
- Image files (`png`, `jpg`, etc.) print through Pillow + pywin32.
- This script is intended for Windows only.
