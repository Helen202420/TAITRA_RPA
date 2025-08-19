import os
from config import CFG
from automation.graph_client import download_to_folder
from automation.dsm_uploader import upload_file_to_dsm

def main():
    # 1) 下載到 download/（沿用遠端檔名）
    local_path = download_to_folder(CFG.DRIVE_ID, CFG.FILE_ID, CFG.DOWNLOAD_DIR)
    print("已下載：", os.path.abspath(local_path))

    # 2) Selenium 登入 DSM 並上傳
    upload_file_to_dsm(
        file_path=os.path.abspath(local_path),
        dsm_url=CFG.DSM_URL,
        username=CFG.DSM_USERNAME,
        password=CFG.DSM_PASSWORD,
        quiet=False,
    )

if __name__ == "__main__":
    main()
