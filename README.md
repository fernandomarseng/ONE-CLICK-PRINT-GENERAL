# ONE-CLICK-PRINT-GENERAL

Windows one-click printing utility for File Explorer workflows.

This project prints all supported files from one folder (non-recursive), either:
- by passing a folder path,
- by choosing a folder from a picker dialog,
- or by setting a default folder in the script.

## Included files

- `one_click_print_general.py` - main script.
- `Run One-Click Print.bat` - launcher you can double-click, run from cmd, or drag/drop a folder onto.
- `Install Context Menu (Show More Options).bat` - adds a File Explorer empty-space right-click entry.
- `Uninstall Context Menu (Show More Options).bat` - removes that entry.
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

### Option D: Add to Explorer "Show more options"

1. Run `Install Context Menu (Show More Options).bat` once.
2. In File Explorer, open any folder.
3. Right-click on empty space in the folder.
4. Click `Show more options`.
5. Click `ONE-CLICK-PRINT-GENERAL`.

To remove it later, run `Uninstall Context Menu (Show More Options).bat`.

### Option E: Manual Registry Editor setup (no installer script)

If you prefer to add the right-click entry manually:

1. Press `Win + R`, type `regedit`, press Enter.
2. Go to:
   - `HKEY_CURRENT_USER\Software\Classes\Directory\Background\shell`
3. Create a new key named:
   - `ONE-CLICK-PRINT-GENERAL`
4. Inside that key, set:
   - `(Default)` = `ONE-CLICK-PRINT-GENERAL`
   - `Icon` (String Value) = `imageres.dll,-5324`
5. Under `ONE-CLICK-PRINT-GENERAL`, create subkey:
   - `command`
6. Set `command` `(Default)` to:
   - `cmd.exe /c ""C:\Users\order entry\OneDrive\Desktop\Programming Projects\ONE-CLICK-PRINT-GENERAL\Run One-Click Print.bat" "%V""`

Notes:
- `%V` passes the current folder path (the folder where you right-clicked empty space).
- If your project folder moves, update the full path in the `command` value.

To remove manually, delete:
- `HKEY_CURRENT_USER\Software\Classes\Directory\Background\shell\ONE-CLICK-PRINT-GENERAL`

## Notes

- PDF and non-image documents use Windows `ShellExecute("print")` unless `PDFtoPrinter.exe` is installed.
- If available at `C:\Program Files\PDFtoPrinter\PDFtoPrinter.exe`, PDFs are sent directly to your selected queue first.
- Image files (`png`, `jpg`, etc.) print through Pillow + pywin32.
- This script is intended for Windows only.
