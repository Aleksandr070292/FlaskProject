from flask import Flask, render_template, request, send_file, abort
import requests
import os
import tempfile

app = Flask(__name__)

YANDEX_DISK_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"

# Функция для получения списка файлов по public_key
def get_files_list(public_key):
    params = {'public_key': public_key}
    try:
        response = requests.get(YANDEX_DISK_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching files list: {e}")
        return None

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Обработчик для получения списка файлов
@app.route('/files', methods=['POST'])
def files():
    public_key = request.form.get('public_key')
    data = get_files_list(public_key)
    if data:
        files = data.get('_embedded', {}).get('items', [])
        return render_template('files.html', files=files)
    return "Не удалось получить список файлов.", 400

# Обработчик для скачивания файла
@app.route('/download')
def download():
    file_url = request.args.get('file_url')
    if not file_url:
        return abort(400, "URL файла отсутствует")

    file_name = file_url.split('/')[-1]
    
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        # Создаем временный файл для сохранения скачанного содержимого
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
            temp_file_path = tmp_file.name

        return send_file(temp_file_path, as_attachment=True, download_name=file_name)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return "Не удалось скачать файл.", 400
    finally:
        # Удаление временного файла после отправки
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == '__main__':
    app.run(debug=True)