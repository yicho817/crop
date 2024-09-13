import tempfile
import shutil

@app.route('/upload', methods=['POST'])
def upload_zip():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 創建臨時目錄
    temp_dir = tempfile.mkdtemp()

    try:
        # 保存並解壓ZIP檔案
        zip_path = os.path.join(temp_dir, file.filename)
        file.save(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # 觸發few-shot learning、模型轉檔和模型部屬
        few_shot_learning(temp_dir)
        convert_model(temp_dir)
        deploy_model(temp_dir)

        return jsonify({"success": "File processed"}), 200
    finally:
        # 清理臨時目錄
        shutil.rmtree(temp_dir)

def few_shot_learning(directory):
    # 實現few-shot learning的邏輯
    pass

def convert_model(directory):
    # 實現模型轉檔的邏輯
    pass

def deploy_model(directory):
    # 實現模型部屬的邏輯
    pass
