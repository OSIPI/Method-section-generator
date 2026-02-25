import os
import shutil
import pydicom
import numpy as np
from fastapi import UploadFile


async def save_upload(upload: UploadFile, base_dir="uploads"):
    """
    Save an uploaded file to the specified base directory.

    Args:
        upload (UploadFile): The uploaded file.
        base_dir (str): The base directory where the file will be saved.

    Returns:
        str: The path to the saved file.
    """

    filename = os.path.basename(upload.filename)
    file_path = os.path.join(base_dir, filename)
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await upload.read())
    return file_path

async def remove_files(file_paths: list):
    """
    Remove a list of files.

    Args:
        file_paths (list): A list of file paths to remove.
    """
    for file_path in file_paths:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")

async def remove_dir(dir_path: str):
    """
    Remove a directory and all its contents.

    Args:
        dir_path (str): The path to the directory to remove.
    """
    try:
        shutil.rmtree(dir_path)
    except Exception as e:
        print(f"Error removing directory {dir_path}: {e}")

def default_serializer(obj):
    """
    Default serializer for non-serializable types.
    """
    # Handle pydicom MultiValue and other non-serializable types
    try:
        if isinstance(obj, pydicom.multival.MultiValue):
            return list(obj)
    except ImportError:
        pass
    # Try to convert numpy types
    try:
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    # Fallback: try to convert to string
    return str(obj)