from flask import Flask, render_template, request, send_file
import requests
import os


app = Flask(__name__)

YANDEX_DISK_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"


# Функция для получения списка файлов по public_key
def get_files_list(public_key):
    params = {'public_key': public_key}
    response = requests.get(YANDEX_DISK_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
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
    file_name = file_url.split('/')[-1]
    response = requests.get(file_url, stream=True)
    with open(file_name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return send_file(file_name, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
