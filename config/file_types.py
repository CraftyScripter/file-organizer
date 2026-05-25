"""File extension categories preserved from the original script."""

from __future__ import annotations

FILE_TYPES: dict[str, list[str]] = {
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
    "text": ["txt", "md", "log", "json", "yaml", "yml", "ini", "cfg", "conf"],
}

EXTENSION_TO_TYPE: dict[str, str] = {
    extension: file_type
    for file_type, extensions in FILE_TYPES.items()
    for extension in extensions
}


def category_for_extension(extension: str) -> str:
    """Return the configured category for an extension, or unknown."""
    return EXTENSION_TO_TYPE.get(extension.lower().lstrip("."), "unknown")
