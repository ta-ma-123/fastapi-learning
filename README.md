# fastapi-learning
FastAPI学習用リポジトリ

## Dev Containersの起動

- VS Codeでコマンドパレットを開く（`Ctrl + Shift + P`）
- 検索欄に以下のコマンドを入力して実行
  ```
  Dev Containers: Reopen in Container
  ```

## FastAPIアプリの実行

Dev Container内のターミナルで、プロジェクト直下から次のコマンドを実行
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

終了する場合、ターミナルで`Ctrl + c`

### ブラウザへアクセス
```
http://localhost:8000/
```

### Swagger UIへアクセス
```
http://localhost:8000/docs/
```

## Dev Containersの再起動
 以下のファイルを変更したときなど
- Dockerfile
- compose.yaml
- devcontainer.json
- requirements.txt

```
Dev Containers: Rebuild and Reopen in Container
```

## Dev Containersの終了
```
Dev Containers: Reopen Folder Locally
```
