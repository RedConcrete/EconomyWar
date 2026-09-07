#!/usr/bin/env python3
"""Extract and repack WC3 .w3x maps using StormLib."""
import ctypes, ctypes.util, os, sys, struct

STORM = ctypes.CDLL("/var/home/fklose/libstorm.so")

# StormLib function signatures
STORM.SFileOpenArchive.restype = ctypes.c_bool
STORM.SFileOpenArchive.argtypes = [ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p)]
STORM.SFileCloseArchive.restype = ctypes.c_bool
STORM.SFileCloseArchive.argtypes = [ctypes.c_void_p]
STORM.SFileFindFirstFile.restype = ctypes.c_void_p
STORM.SFileFindFirstFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_char_p]
STORM.SFileFindNextFile.restype = ctypes.c_bool
STORM.SFileFindNextFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
STORM.SFileFindClose.restype = ctypes.c_bool
STORM.SFileFindClose.argtypes = [ctypes.c_void_p]
STORM.SFileExtractFile.restype = ctypes.c_bool
STORM.SFileExtractFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
STORM.SFileCreateArchive.restype = ctypes.c_bool
STORM.SFileCreateArchive.argtypes = [ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p)]
STORM.SFileAddFileEx.restype = ctypes.c_bool
STORM.SFileAddFileEx.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]

# SFILE_FIND_DATA structure (simplified, name is first 1024 bytes)
class SFILE_FIND_DATA(ctypes.Structure):
    _fields_ = [
        ("cFileName", ctypes.c_char * 1024),
        ("szPlainName", ctypes.c_char_p),
        ("dwHashIndex", ctypes.c_uint),
        ("dwBlockIndex", ctypes.c_uint),
        ("dwFileSize", ctypes.c_uint),
        ("dwFileFlags", ctypes.c_uint),
        ("dwCompSize", ctypes.c_uint),
        ("dwFileTimeLo", ctypes.c_uint),
        ("dwFileTimeHi", ctypes.c_uint),
        ("lcLocale", ctypes.c_uint),
    ]

MPQ_OPEN_NO_ATTRIBUTES = 0x00000100
MPQ_FILE_COMPRESS = 0x00000200


def extract(map_path: str, out_dir: str):
    hMpq = ctypes.c_void_p()
    if not STORM.SFileOpenArchive(map_path.encode(), 0, MPQ_OPEN_NO_ATTRIBUTES, ctypes.byref(hMpq)):
        print("SFileOpenArchive failed")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    fd = SFILE_FIND_DATA()
    hFind = STORM.SFileFindFirstFile(hMpq, b"*", ctypes.byref(fd), None)
    if not hFind:
        print("No files found")
        STORM.SFileCloseArchive(hMpq)
        return

    while True:
        name = fd.cFileName.decode("utf-8", errors="replace")
        if not name.startswith("("):
            out_path = os.path.join(out_dir, name.replace("\\", "/"))
            os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else out_dir, exist_ok=True)
            ok = STORM.SFileExtractFile(hMpq, name.encode(), out_path.encode(), 0)
            print(f"{'OK' if ok else 'FAIL'}: {name}")
        if not STORM.SFileFindNextFile(hFind, ctypes.byref(fd)):
            break

    STORM.SFileFindClose(hFind)
    STORM.SFileCloseArchive(hMpq)


def repack(src_dir: str, out_map: str, max_files: int = 1024):
    """Repack extracted directory back into .w3x"""
    import tempfile, shutil

    # Read original WC3 512-byte header from extracted dir parent
    orig_map = out_map.replace("_repacked", "").replace(".w3x", "")
    # We'll write MPQ only; caller must prepend HM3W header if needed

    hMpq = ctypes.c_void_p()
    MPQ_CREATE_ARCHIVE_V1 = 0x00010000
    if not STORM.SFileCreateArchive(out_map.encode(), MPQ_CREATE_ARCHIVE_V1, max_files, ctypes.byref(hMpq)):
        print("SFileCreateArchive failed")
        sys.exit(1)

    for root, dirs, files in os.walk(src_dir):
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, src_dir).replace("/", "\\")
            ok = STORM.SFileAddFileEx(hMpq, full.encode(), rel.encode(), MPQ_FILE_COMPRESS, 8, 0)
            print(f"{'ADD' if ok else 'FAIL'}: {rel}")

    STORM.SFileCloseArchive(hMpq)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "extract" and len(sys.argv) == 4:
        extract(sys.argv[2], sys.argv[3])
    elif cmd == "repack" and len(sys.argv) == 4:
        repack(sys.argv[2], sys.argv[3])
    else:
        print("Usage:")
        print("  python3 w3x_tool.py extract <map.w3x> <out_dir>")
        print("  python3 w3x_tool.py repack  <src_dir>  <out.w3x>")
