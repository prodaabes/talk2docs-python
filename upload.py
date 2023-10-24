from typing import List
from fastapi import UploadFile
from pathlib import Path
import shutil

def upload(ownerId: str, files: List[UploadFile]):
    for file in files:
        try:

            file_parent_path = "temp/" + ownerId
            Path(file_parent_path).mkdir(parents=True, exist_ok=True)

            file_path = file_parent_path + "/" + file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                    
        except Exception as e:
            print(str(e))