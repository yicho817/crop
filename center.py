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
    # 假設有個train.py腳本負責訓練模型
    os.system(f"python train.py --data_dir {directory}")

def convert_model(directory):
    # 假設有個convert.py腳本負責模型轉檔
    os.system(f"python convert.py --model_dir {directory}")

def deploy_model(directory):
    # 假設有個deploy.py腳本負責模型部屬
    os.system(f"python deploy.py --model_dir {directory}")
curl -X POST http://127.0.0.1:5000/upload -F 'file=@path/to/your/file.zip'
