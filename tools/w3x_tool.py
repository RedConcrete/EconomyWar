#!/usr/bin/env python3
"""Extract and patch WC3 .w3x maps using StormLib."""
import ctypes, os, sys, shutil

STORM = ctypes.CDLL("/var/home/fklose/libstorm.so")

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
STORM.SFileAddFileEx.restype = ctypes.c_bool
STORM.SFileAddFileEx.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]

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

MPQ_OPEN_NO_ATTRIBUTES   = 0x00000100
MPQ_FILE_COMPRESS        = 0x00000200
MPQ_FILE_REPLACEEXISTING = 0x80000000


def extract(map_path: str, out_dir: str):
    hMpq = ctypes.c_void_p()
    if not STORM.SFileOpenArchive(map_path.encode(), 0, MPQ_OPEN_NO_ATTRIBUTES, ctypes.byref(hMpq)):
        print("SFileOpenArchive failed"); sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    fd = SFILE_FIND_DATA()
    hFind = STORM.SFileFindFirstFile(hMpq, b"*", ctypes.byref(fd), None)
    if not hFind:
        STORM.SFileCloseArchive(hMpq); return

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


def patch(src_map: str, out_map: str, files: dict):
    """Copy src_map to out_map and replace/add specific files.
    files = { 'archive_path': 'local_file_path' }
    """
    shutil.copy2(src_map, out_map)

    hMpq = ctypes.c_void_p()
    if not STORM.SFileOpenArchive(out_map.encode(), 0, 0, ctypes.byref(hMpq)):
        print("SFileOpenArchive (write) failed"); sys.exit(1)

    for archive_name, local_path in files.items():
        if not os.path.isfile(local_path):
            print(f"SKIP (not found): {local_path}")
            continue
        flags = MPQ_FILE_COMPRESS | MPQ_FILE_REPLACEEXISTING
        ok = STORM.SFileAddFileEx(
            hMpq,
            local_path.encode(),
            archive_name.encode(),
            flags,
            2,   # MPQ_COMPRESSION_ZLIB
            0
        )
        print(f"{'PATCH' if ok else 'FAIL'}: {archive_name}")

    STORM.SFileCloseArchive(hMpq)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "extract" and len(sys.argv) == 4:
        extract(sys.argv[2], sys.argv[3])
    elif cmd == "patch" and len(sys.argv) >= 4:
        # patch <src.w3x> <out.w3x> [archive_name=local_file ...]
        files = {}
        for pair in sys.argv[4:]:
            k, v = pair.split("=", 1)
            files[k] = v
        patch(sys.argv[2], sys.argv[3], files)
    else:
        print("Usage:")
        print("  python3 w3x_tool.py extract <map.w3x> <out_dir>")
        print("  python3 w3x_tool.py patch   <src.w3x> <out.w3x> [archive_name=local_file ...]")
