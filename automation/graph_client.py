import os
import requests
import msal
from config import CFG  # ← 從根目錄的 config 取設定

def _get_access_token() -> str:
    """以 App-only 流程拿 Graph token。"""
    app = msal.ConfidentialClientApplication(
        CFG.CLIENT_ID,
        authority=CFG.AUTHORITY,
        client_credential=CFG.CLIENT_SECRET,
    )
    tok = app.acquire_token_for_client(scopes=CFG.SCOPES)
    if "access_token" not in tok:
        raise SystemExit(f"取 Token 失敗：{tok}")
    return tok["access_token"]

def _get(url: str, headers: dict) -> requests.Response:
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r

def download_to_folder(drive_id: str, file_id: str, download_dir: str) -> str:
    """
    下載指定 drive 的指定檔案到 download_dir。
    回傳下載後的本機完整路徑。
    """
    os.makedirs(download_dir, exist_ok=True)
    access_token = _get_access_token()
    H = {"Authorization": f"Bearer {access_token}"}

    # 驗證這顆 drive 可讀
    _get(f"https://graph.microsoft.com/v1.0/drives/{drive_id}?$select=id,name,webUrl", H)

    # 取檔案名稱與可能的匿名下載連結
    meta = _get(
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}"
        "?$select=id,name,@microsoft.graph.downloadUrl",
        H,
    ).json()
    filename = meta["name"]
    out_path = os.path.join(download_dir, filename)

    # 先用匿名下載連結（有就不需帶權杖）
    anon = meta.get("@microsoft.graph.downloadUrl")
    if anon:
        raw = requests.get(anon)
        raw.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(raw.content)
        return out_path

    # 沒有匿名連結就走受保護的 /content 端點
    content = _get(
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/content",
        H,
    ).content
    with open(out_path, "wb") as f:
        f.write(content)
    return out_path
