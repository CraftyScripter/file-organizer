# File Organizer

This Python script organizes files in a directory into subdirectories based on their file types. It categorizes files into predefined types such as documents, images, videos, audio, spreadsheets, presentations, archives, executables, web files, databases, and text files.

## Features

- Automatically categorizes files based on their extensions.
- Creates subdirectories for each file type if they do not already exist.
- Moves files into their respective subdirectories.

## File Types Supported

The script categorizes files into the following types:

- **Document:** `doc`, `docx`, `pdf`, `odt`, `rtf`, `tex`, `wpd`, `wks`, `wps`, `pages`
- **Image:** `jpg`, `jpeg`, `png`, `gif`, `bmp`, `svg`, `tiff`, `tif`, `psd`, `ai`, `eps`, `raw`, `cr2`, `nef`, `orf`, `sr2`, `ico`, `heic`
- **Video:** `mp4`, `avi`, `mkv`, `mov`, `flv`, `wmv`, `mpg`, `mpeg`, `3gp`, `webm`, `vob`, `ogv`, `m4v`
- **Audio:** `mp3`, `wav`, `aac`, `flac`, `ogg`, `wma`, `m4a`, `aiff`, `au`, `pcm`, `aif`, `midi`, `mid`
- **Spreadsheet:** `xls`, `xlsx`, `csv`, `ods`, `xlr`, `xlt`, `xlsm`
- **Presentation:** `ppt`, `pptx`, `odp`, `key`, `pps`, `ppsx`, `pptm`
- **Archive:** `zip`, `rar`, `tar`, `gz`, `7z`, `bz2`, `xz`, `iso`, `dmg`, `tgz`, `cab`, `lz`, `jar`
- **Executable:** `exe`, `bat`, `sh`, `bin`, `apk`, `com`, `msi`, `gadget`, `wsf`
- **Web:** `html`, `htm`, `css`, `js`, `php`, `asp`, `aspx`, `jsp`, `cfm`, `xml`, `rss`, `xhtml`
- **Database:** `sql`, `db`, `mdb`, `accdb`, `sqlite`, `dbf`, `pdb`, `sqlitedb`
- **Text:** `txt`, `md`, `log`, `json`, `yaml`, `yml`, `ini`, `cfg`, `conf`

## Requirements

- Python 3.x
- `os` and `shutil` modules (included with Python standard library)

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/file-organizer.git
    cd file-organizer
    ```

2. **Install Python:**

    - **Windows:**
      Download and install Python from [python.org](https://www.python.org/downloads/). Ensure you check the box to add Python to your PATH during installation.

    - **Linux:**
      Python is often pre-installed. If not, you can install it using your package manager. For example, on Ubuntu:

      ```bash
      sudo apt update
      sudo apt install python3
      ```

## Usage

1. **Edit the script to set the target directory:**

    Open `file_organizer.py` in a text editor and update the `directory_to_organize` variable with the path of the directory you want to organize.

    ```python
    directory_to_organize = r'path to target directory'
    ```

    - **Windows:** Use double backslashes (`\\`) or raw string notation (prefix the string with `r`) for the directory path. Example: `r'C:\Users\YourUsername\Downloads'`
    - **Linux:** Use forward slashes (`/`) for the directory path. Example: `'/home/yourusername/Downloads'`

2. **Run the script:**

    Open a terminal or command prompt and execute the script:

    ```bash
    python file_organizer.py
    ```

    - **Windows:** You may need to use `python` or `python3` depending on your installation.
    - **Linux:** Typically, you can use `python3` if Python 2 is also installed. 
