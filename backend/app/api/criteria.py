import shutil
import pandas as pd
import fitz  # PyMuPDF
import markdown
from bs4 import BeautifulSoup
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

router = APIRouter()

# UPLOAD_DIRをbackendディレクトリからの相対パスに変更
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploaded_criteria"
UPLOAD_DIR.mkdir(exist_ok=True)

# --- Parser Functions --- #

def _parse_csv_xlsx(file_path: Path):
    """CSVまたはXLSXファイルを解析して評価基準リストを返す"""
    try:
        df = pd.read_excel(file_path) if file_path.suffix == '.xlsx' else pd.read_csv(file_path)
        # 想定される列名で抽出を試みる
        if '要件/構成要素' in df.columns and '定義' in df.columns:
            df_filtered = df[['要件/構成要素', '定義']].dropna()
            return [
                {"name": row[0], "definition": row[1], "score": 3, "memo": ""}
                for row in df_filtered.itertuples(index=False)
            ]
        # 上記が失敗した場合、最初の2列を単純に使う
        else:
            df_filtered = df.iloc[:, [0, 1]].dropna()
            return [
                {"name": row[0], "definition": row[1], "score": 3, "memo": ""}
                for row in df_filtered.itertuples(index=False)
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル解析エラー: {e}")

def _parse_md(file_path: Path):
    """Markdownファイルを解析して評価基準リストを返す"""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            md_text = f.read()
        
        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, "html.parser")
        
        criteria = []
        # h2またはh3タグを見出しと仮定
        for header in soup.find_all(["h2", "h3"]):
            name = header.get_text(strip=True)
            # ヘッダーの次にあるpタグを定義と仮定
            p_tag = header.find_next_sibling("p")
            if name and p_tag:
                definition = p_tag.get_text(strip=True)
                criteria.append({"name": name, "definition": definition, "score": 3, "memo": ""})
        
        if not criteria:
            raise HTTPException(status_code=400, detail="Markdownファイルから有効な評価基準が見つかりませんでした。h2/h3を見出し、pを定義としてください。")

        return criteria
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Markdownファイル解析エラー: {e}")

def _parse_pdf(file_path: Path):
    """PDFファイルを解析して評価基準リストを返す"""
    try:
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        criteria = []
        lines = full_text.split('\n')
        current_item = None

        for line in lines:
            line = line.strip()
            if not line: continue

            # 箇条書きの始まりを検出 (簡易的な正規表現)
            import re
            if re.match(r"^(■|●|・|\d+\.|\*|-)", line):
                if current_item:
                    criteria.append(current_item)
                
                current_item = {
                    "name": line,
                    "definition": "",
                    "score": 3,
                    "memo": ""
                }
            elif current_item:
                current_item["definition"] += line + " "
        
        if current_item:
            criteria.append(current_item)

        # 整形
        for item in criteria:
            item["definition"] = item["definition"].strip()

        if not criteria:
            raise HTTPException(status_code=400, detail="PDFファイルから有効な評価基準が見つかりませんでした。箇条書き形式で記述してください。")

        return criteria
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDFファイル解析エラー: {e}")

# --- API Endpoints --- #


@router.post("/upload")
async def upload_criteria_file(file: UploadFile = File(...)):
    """
    評価基準ファイルをアップロードします。
    対応形式: .csv, .xlsx, .pdf, .md, .docx
    """
    allowed_extensions = {".csv", ".xlsx", ".pdf", ".md", ".docx"}
    file_extension = Path(file.filename).suffix

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"無効なファイル形式です。対応している形式: {', '.join(allowed_extensions)}"
        )

    # 安全なファイル名を生成（ディレクトリトラバーサル対策）
    safe_filename = Path(file.filename).name
    destination = UPLOAD_DIR / safe_filename

    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"ファイルの保存中にエラーが発生しました: {e}"
        )
    finally:
        file.file.close()

    return {
        "filename": safe_filename,
        "content_type": file.content_type,
        "message": "ファイルが正常にアップロードされました。"
    }

@router.get("/")
async def get_criteria_files():
    """
    アップロード済みの評価基準ファイルの一覧を取得します。
    """
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            files.append(file_path.name)
    return files

@router.get("/{filename}")
async def get_criteria_definition(filename: str):
    """
    指定された評価基準ファイルの内容を解析してJSON形式で返します。
    """
    file_path = UPLOAD_DIR / Path(filename).name
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    file_extension = file_path.suffix
    if file_extension in [".csv", ".xlsx"]:
        return _parse_csv_xlsx(file_path)
    elif file_extension == ".md":
        return _parse_md(file_path)
    elif file_extension == ".pdf":
        return _parse_pdf(file_path)
    else:
        raise HTTPException(status_code=400, detail=f"サポートされていないファイル形式です: {file_extension}")

@router.delete("/{filename}")
async def delete_criteria_file(filename: str):
    """
    指定された評価基準ファイルを削除します。
    """
    # ディレクトリトラバーサル攻撃を防ぐ
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="無効なファイル名です")

    file_path = UPLOAD_DIR / filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    try:
        file_path.unlink()
        return {"message": f"ファイル '{filename}' が正常に削除されました。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルの削除中にエラーが発生しました: {e}")
