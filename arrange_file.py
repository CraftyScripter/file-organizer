file_types = {
    "document": ["doc", "docx", "pdf", "odt", "rtf", "tex", "wpd", "wks", "wps", "pages"],
    "image": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "tiff", "tif", "psd", "ai", "eps", "raw", "cr2", "nef", "orf", "sr2", "ico", "heic"],
    "video": ["mp4", "avi", "mkv", "mov", "flv", "wmv", "mpg", "mpeg", "3gp", "webm", "vob", "ogv", "m4v"],
    "audio": ["mp3", "wav", "aac", "flac", "ogg", "wma", "m4a", "aiff", "au", "pcm", "aif", "midi", "mid"],
    "spreadsheet": ["xls", "xlsx", "csv", "ods", "xlr", "xlt", "xlsm"],
    "presentation": ["ppt", "pptx", "odp", "key", "pps", "ppsx", "pptm"],
    "archive": ["zip", "rar", "tar", "gz", "7z", "bz2", "xz", "iso", "dmg", "tgz", "cab", "lz", "jar"],
    "executable": ["exe", "bat", "sh", "bin", "apk", "com", "msi", "gadget", "wsf"],
    "web": ["html", "htm", "css", "js", "php", "asp", "aspx", "jsp", "cfm", "xml", "rss", "xhtml"],
    "database": ["sql", "db", "mdb", "accdb", "sqlite", "dbf", "pdb", "sqlitedb"],
    "text": ["txt", "md", "log", "json", "yaml", "yml", "ini", "cfg", "conf"]
}

import os
import shutil

# Inverse dictionary for quick lookup
extension_to_type = {ext: file_type for file_type, exts in file_types.items() for ext in exts}

def get_file_type(extension):
    return extension_to_type.get(extension.lower(), "unknown")

def move_file_to_folder(file_path, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    shutil.move(file_path, os.path.join(destination_folder, os.path.basename(file_path)))

def organize_files_in_directory(directory):
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(file_name)
            ext = ext.lstrip('.').lower()  # Remove leading dot and convert to lowercase
            file_type = get_file_type(ext)
            if file_type != "unknown":
                destination_folder = os.path.join(directory, file_type)
                move_file_to_folder(file_path, destination_folder)

# Example usage
directory_to_organize = r'path to target directory'  ## example - C:\Users\<user name>\Downloads
organize_files_in_directory(directory_to_organize)   


