#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import cgi
import os
import shutil
import html
from datetime import datetime

PORT = 8000
UPLOAD_DIR = "uploads"  # مجلد مخصص للاستقبال

# إنشاء مجلد الرفع إذا لم يكن موجوداً
os.makedirs(UPLOAD_DIR, exist_ok=True)

# البانر الخاص بك (NIGHT LINUX)
BANNER = """
\033[96m
███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗
████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝
██╔██╗ ██║██║██║  ███╗███████║   ██║   
██║╚██╗██║██║██║   ██║██╔══██║   ██║   
██║ ╚████║██║╚██████╔╝██║  ██║   ██║   
╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
                                       
██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗ 
██║     ██║████╗  ██║██║   ██║╚██╗██╔╝ 
██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝  
██║     ██║██║╚██╗██║██║   ██║ ██╔██╗  
███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗ 
╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝ 
\033[0m
"""

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html_content = self.get_html_page()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            # خدمة الملفات المرفوعة (عرضها)
            super().do_GET()

    def do_POST(self):
        try:
            # استخدام FieldStorage الذي يتعامل مع الملفات الكبيرة (يكتبها على القرص)
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers.get('Content-Type', '')}
            )
            if 'file' not in form:
                self.send_error(400, "لا يوجد ملف مرفق")
                return

            file_items = form['file']
            # إذا كان ملف واحد فقط، نجعله قائمة
            if not isinstance(file_items, list):
                file_items = [file_items]

            uploaded_files = []
            for file_item in file_items:
                if file_item.filename:
                    filename = os.path.basename(file_item.filename)
                    # تجنب الكتابة فوق ملف موجود
                    safe_name = filename
                    counter = 1
                    while os.path.exists(os.path.join(UPLOAD_DIR, safe_name)):
                        name, ext = os.path.splitext(filename)
                        safe_name = f"{name}_{counter}{ext}"
                        counter += 1
                    filepath = os.path.join(UPLOAD_DIR, safe_name)
                    # حفظ الملف: إذا كان الملف مؤقتاً، ننقله
                    if file_item.file:
                        with open(filepath, 'wb') as dest:
                            shutil.copyfileobj(file_item.file, dest)
                    else:
                        # في حالة كان الملف صغيراً وتخزينه في الذاكرة
                        with open(filepath, 'wb') as dest:
                            dest.write(file_item.value)
                    file_size = os.path.getsize(filepath)
                    uploaded_files.append({
                        'name': safe_name,
                        'size': file_size,
                        'path': filepath
                    })

            # إرسال رد JSON بنجاح
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            import json
            response = {
                'status': 'success',
                'files': [{'name': f['name'], 'size': f['size']} for f in uploaded_files],
                'message': f"تم رفع {len(uploaded_files)} ملف بنجاح"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            import json
            response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(response).encode('utf-8'))

    def get_html_page(self):
        # صفحة HTML جميلة مع شريط تقدم ودعم رفع متعدد
        return f'''<!DOCTYPE html>
<html lang="ar" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>NIGHT LINUX - رفع الملفات</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: rgba(15, 25, 45, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 28px;
            padding: 30px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 25px 45px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{
            text-align: center;
            color: #00d4ff;
            font-size: 2rem;
            margin-bottom: 10px;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(0,212,255,0.5);
        }}
        .sub {{
            text-align: center;
            color: #8e9aaf;
            margin-bottom: 30px;
            font-size: 0.9rem;
        }}
        .upload-area {{
            border: 2px dashed #2c3e66;
            border-radius: 20px;
            padding: 30px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }}
        .upload-area:hover {{
            border-color: #00d4ff;
            background: rgba(0,212,255,0.05);
        }}
        .upload-area.drag-over {{
            border-color: #00ffaa;
            background: rgba(0,255,170,0.1);
        }}
        .upload-icon {{
            font-size: 48px;
            margin-bottom: 15px;
            color: #5c6e91;
        }}
        .file-input {{
            display: none;
        }}
        .btn {{
            background: linear-gradient(45deg, #1e2a4a, #0f172a);
            border: none;
            color: white;
            padding: 12px 28px;
            border-radius: 40px;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
            margin: 5px;
            font-weight: bold;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .btn-primary {{
            background: linear-gradient(45deg, #00a6c4, #0088aa);
            box-shadow: 0 4px 15px rgba(0,168,196,0.3);
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            filter: brightness(1.05);
        }}
        .btn-danger {{
            background: linear-gradient(45deg, #8b2c2c, #5c1e1e);
        }}
        .file-list {{
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .file-item {{
            background: rgba(255,255,255,0.05);
            border-radius: 14px;
            padding: 12px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(5px);
            transition: 0.2s;
        }}
        .file-info {{
            flex: 1;
            word-break: break-word;
        }}
        .file-name {{
            font-weight: bold;
            color: #cbd5e6;
        }}
        .file-size {{
            font-size: 0.75rem;
            color: #7e8cac;
        }}
        .progress {{
            background: #1e2a3a;
            border-radius: 20px;
            height: 8px;
            width: 100%;
            margin-top: 8px;
            overflow: hidden;
        }}
        .progress-bar {{
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #00ffaa);
            transition: width 0.2s ease;
        }}
        .status {{
            margin-top: 15px;
            text-align: center;
            color: #a0b3d9;
            font-size: 0.9rem;
        }}
        footer {{
            text-align: center;
            margin-top: 25px;
            font-size: 0.7rem;
            color: #3e4a66;
        }}
        a {{
            color: #00d4ff;
            text-decoration: none;
        }}
        @media (max-width: 500px) {{
            .container {{
                padding: 20px;
            }}
            .btn {{
                padding: 8px 16px;
            }}
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>⚡ NIGHT LINUX</h1>
    <div class="sub">نقل الملفات عبر الشبكة المحلية</div>

    <div class="upload-area" id="dropzone">
        <div class="upload-icon">📁</div>
        <div>اسحب الملفات هنا أو انقر للاختيار</div>
        <input type="file" id="fileInput" multiple class="file-input">
        <div style="margin-top: 15px;">
            <button class="btn" id="selectBtn">اختر ملفات</button>
            <button class="btn btn-primary" id="uploadBtn" disabled>رفع (0)</button>
            <button class="btn btn-danger" id="clearBtn">تفريغ</button>
        </div>
    </div>

    <div class="file-list" id="fileList"></div>
    <div class="status" id="status"></div>
    <footer>🖥️ الخادم يعمل على <span id="serverIp"></span> : {{PORT}}<br>تم تطويره بواسطة NIGHT LINUX</footer>
</div>

<script>
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const selectBtn = document.getElementById('selectBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const clearBtn = document.getElementById('clearBtn');
    const fileListDiv = document.getElementById('fileList');
    const statusDiv = document.getElementById('status');

    let selectedFiles = [];

    // عرض IP الخادم
    fetch('/server-ip')
        .then(r => r.text())
        .catch(() => window.location.hostname)
        .then(ip => {{
            document.getElementById('serverIp').innerText = window.location.hostname || ip;
        }});

    function formatBytes(bytes) {{
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }}

    function updateFileList() {{
        fileListDiv.innerHTML = '';
        if (selectedFiles.length === 0) {{
            fileListDiv.innerHTML = '<div style="text-align:center;color:#5c6e91;">لا توجد ملفات محددة</div>';
            uploadBtn.disabled = true;
            uploadBtn.innerText = 'رفع (0)';
            return;
        }}
        uploadBtn.disabled = false;
        uploadBtn.innerText = `رفع (${{selectedFiles.length}})`;
        selectedFiles.forEach((file, idx) => {{
            const div = document.createElement('div');
            div.className = 'file-item';
            div.innerHTML = `
                <div class="file-info">
                    <div class="file-name">${{escapeHtml(file.name)}}</div>
                    <div class="file-size">${{formatBytes(file.size)}}</div>
                    <div class="progress"><div class="progress-bar" id="progress-${{idx}}" style="width:0%"></div></div>
                </div>
                <button class="btn" style="background:#3a2a2a; padding:4px 12px;" onclick="removeFile(${{idx}})">✖</button>
            `;
            fileListDiv.appendChild(div);
        }});
    }}

    function escapeHtml(str) {{
        return str.replace(/[&<>]/g, function(m) {{
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        }});
    }}

    window.removeFile = function(index) {{
        selectedFiles.splice(index, 1);
        updateFileList();
    }};

    function addFiles(files) {{
        for (let file of files) {{
            selectedFiles.push(file);
        }}
        updateFileList();
    }}

    selectBtn.onclick = () => fileInput.click();
    fileInput.onchange = (e) => addFiles(Array.from(e.target.files));
    clearBtn.onclick = () => {{
        selectedFiles = [];
        fileInput.value = '';
        updateFileList();
        statusDiv.innerHTML = '';
    }};

    // Drag & Drop
    dropzone.addEventListener('dragover', (e) => {{
        e.preventDefault();
        dropzone.classList.add('drag-over');
    }});
    dropzone.addEventListener('dragleave', () => {{
        dropzone.classList.remove('drag-over');
    }});
    dropzone.addEventListener('drop', (e) => {{
        e.preventDefault();
        dropzone.classList.remove('drag-over');
        addFiles(Array.from(e.dataTransfer.files));
    }});
    dropzone.addEventListener('click', () => fileInput.click());

    async function uploadFiles() {{
        if (selectedFiles.length === 0) return;
        statusDiv.innerHTML = '⏳ جاري الرفع... لا تغلق الصفحة';
        const totalFiles = selectedFiles.length;
        let completed = 0;

        for (let i = 0; i < totalFiles; i++) {{
            const file = selectedFiles[i];
            const formData = new FormData();
            formData.append('file', file);

            try {{
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/', true);
                xhr.upload.onprogress = (event) => {{
                    if (event.lengthComputable) {{
                        const percent = (event.loaded / event.total) * 100;
                        const progressBar = document.getElementById(`progress-${{i}}`);
                        if (progressBar) progressBar.style.width = percent + '%';
                    }}
                }};
                await new Promise((resolve, reject) => {{
                    xhr.onload = () => {{
                        if (xhr.status === 200) resolve();
                        else reject(new Error(xhr.statusText));
                    }};
                    xhr.onerror = () => reject(new Error('فشل الاتصال'));
                    xhr.send(formData);
                }});
                completed++;
                // تحديث شريط التقدم إذا أردنا إظهار تقدم كلي
                const progressBar = document.getElementById(`progress-${{i}}`);
                if (progressBar) progressBar.style.width = '100%';
                statusDiv.innerHTML = `✅ تم رفع ${{completed}} من ${{totalFiles}} ملفات`;
            }} catch (err) {{
                statusDiv.innerHTML = `❌ فشل رفع ${{file.name}}: ${{err.message}}`;
                const progressBar = document.getElementById(`progress-${{i}}`);
                if (progressBar) progressBar.style.backgroundColor = '#ff4444';
            }}
        }}

        if (completed === totalFiles) {{
            statusDiv.innerHTML = '🎉 تم رفع جميع الملفات بنجاح!';
            selectedFiles = [];
            fileInput.value = '';
            updateFileList();
        }}
    }}

    uploadBtn.onclick = uploadFiles;

    // إضافة نقطة نهاية للحصول على IP (اختياري)
    // لطباعة عنوان الخادم في وحدة التحكم
    console.log('NIGHT LINUX Uploader ready');
</script>
</body>
</html>
'''

# نقطة نهاية إضافية لمعرفة IP الخادم (اختياري ولكن مفيد)
class CustomTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_server():
    print(BANNER)
    print(f"\033[92m🚀 خادم NIGHT LINUX يعمل على المنفذ {PORT}\033[0m")
    print(f"\033[93m📂 سيتم حفظ الملفات في المجلد: {os.path.abspath(UPLOAD_DIR)}\033[0m")
    print(f"\033[96m📱 افتح على هاتفك: http://<عنوان_اللاب_IP>:{PORT}\033[0m")
    print("\033[90mاضغط Ctrl+C للإيقاف\033[0m")
    with CustomTCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\033[91mتم إيقاف الخادم\033[0m")

if __name__ == "__main__":
    run_server()
