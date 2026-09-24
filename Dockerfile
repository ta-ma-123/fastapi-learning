# Python 3.12の軽量イメージを使用する
FROM python:3.12-slim

# コンテナ内の作業ディレクトリを設定する
WORKDIR /app

# Pythonの依存ライブラリをインストールする
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# FastAPIのソースコードをイメージに組み込む
COPY app/ ./app/

# Alembicのマイグレーションに必要なファイルを組み込む
COPY alembic.ini .
COPY migrations/ ./migrations/

# STEP 8で作成したテストコードを組み込む
COPY tests/ ./tests/

# アプリケーションが使用するポートを明示する
EXPOSE 8000

# コンテナ起動時にFastAPIを実行する
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
