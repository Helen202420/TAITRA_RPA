import os
from dotenv import load_dotenv

load_dotenv()  # 讀取 .env（不要提交到 Git）

class _Config:
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPES = ["https://graph.microsoft.com/.default"]

    DRIVE_ID = os.getenv("DRIVE_ID")
    FILE_ID  = os.getenv("FILE_ID")

    DSM_URL = os.getenv("DSM_URL")
    DSM_USERNAME = os.getenv("DSM_USERNAME")
    DSM_PASSWORD = os.getenv("DSM_PASSWORD")

    # 下載資料夾（預設為專案根目錄下的 download/）
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", os.path.join(BASE_DIR, "download"))

    def validate(self):
        required = {
            "TENANT_ID": self.TENANT_ID,
            "CLIENT_ID": self.CLIENT_ID,
            "CLIENT_SECRET": self.CLIENT_SECRET,
            "DRIVE_ID": self.DRIVE_ID,
            "FILE_ID": self.FILE_ID,
            "DSM_URL": self.DSM_URL,
            "DSM_USERNAME": self.DSM_USERNAME,
            "DSM_PASSWORD": self.DSM_PASSWORD,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise SystemExit(f"環境變數缺少：{', '.join(missing)}")

CFG = _Config()
CFG.validate()
