import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import threading
import time
import binascii
import csv
import json
import os

def get_com_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def reload_ports():
    ports = get_com_ports()
    com_port_cb['values'] = ports
    if ports:
        com_port_cb.current(0)
    else:
        com_port_cb.set('')

ser = None
stop_thread = False
received_data = []
SETUP_FILE = 'setup.json'

LANGUAGES = {
    'en': 'English',
    'zh_tw': '繁體中文',
    'zh_cn': '简体中文',
    'es': 'Español',
    'pt': 'Português',
}

STRINGS = {
    'en': {
        'title': 'COM Port Tool',
        'com_port': 'COM Port:',
        'reload': 'Reload',
        'baudrate': 'Baudrate:',
        'connect': 'Connect',
        'disconnect': 'Disconnect',
        'send': 'Send',
        'send_label': 'Send:',
        'display_format': 'Display:',
        'clear': 'Clear',
        'save': 'Save',
        'save_format': 'Format',
        'clear_settings': 'Reset',
        'status_ready': 'Ready.',
        'help': 'Help',
        'teaching': 'Tutorial',
        'close': 'Close',
    },
    'zh_tw': {
        'title': 'COM Port 連線工具',
        'com_port': 'COM 連接埠:',
        'reload': '重新整理',
        'baudrate': '速度:',
        'connect': '連線',
        'disconnect': '斷線',
        'send': '傳送',
        'send_label': '傳送:',
        'display_format': '顯示格式:',
        'clear': '清除',
        'save': '儲存',
        'save_format': '格式',
        'clear_settings': '請清除',
        'status_ready': '就緒。',
        'help': '說明',
        'teaching': '教學',
        'close': '關閉',
    },
    'zh_cn': {
        'title': 'COM Port 连接工具',
        'com_port': 'COM 端口:',
        'reload': '刷新',
        'baudrate': '速度:',
        'connect': '连接',
        'disconnect': '断开',
        'send': '发送',
        'send_label': '发送:',
        'display_format': '显示格式:',
        'clear': '清除',
        'save': '保存',
        'save_format': '格式',
        'clear_settings': '请清除',
        'status_ready': '就绪。',
        'help': '说明',
        'teaching': '教学',
        'close': '关闭',
    },
    'es': {
        'title': 'Herramienta de Puerto COM',
        'com_port': 'Puerto COM:',
        'reload': 'Recargar',
        'baudrate': 'Velocidad:',
        'connect': 'Conectar',
        'disconnect': 'Desconectar',
        'send': 'Enviar',
        'send_label': 'Enviar:',
        'display_format': 'Formato:',
        'clear': 'Limpiar',
        'save': 'Guardar',
        'save_format': 'Formato',
        'clear_settings': 'Restablecer',
        'status_ready': 'Listo.',
        'help': 'Ayuda',
        'teaching': 'Tutorial',
        'close': 'Cerrar',
    },
    'pt': {
        'title': 'Ferramenta de Porta COM',
        'com_port': 'Porta COM:',
        'reload': 'Recarregar',
        'baudrate': 'Velocidade:',
        'connect': 'Conectar',
        'disconnect': 'Desconectar',
        'send': 'Enviar',
        'send_label': 'Enviar:',
        'display_format': 'Formato:',
        'clear': 'Limpar',
        'save': 'Salvar',
        'save_format': 'Formato',
        'clear_settings': 'Redefinir',
        'status_ready': 'Pronto.',
        'help': 'Ajuda',
        'teaching': 'Tutorial',
        'close': 'Fechar',
    },
}

TEACHING_TEXTS = {
    'en': """
How to send data:
- string: Enter text directly, e.g. Hello123\r\n
- hex: Enter hexadecimal string (case-insensitive, spaces allowed), e.g. 48 65 6C 6C 6F 31 32 33 0D 0A
- decimal: Enter decimal string (each byte separated by space), e.g. 72 101 108 108 111 49 50 51 13 10
\nSelect display format, enter the corresponding content, then press Send.
www.powenko.com 柯博文老師
""",
    'zh_tw': """
【教學】如何傳送資料：
- string：直接輸入要傳送的文字，例如 Hello123\r\n
- hex：輸入十六進位字串（不分大小寫、可有空白），例如 48 65 6C 6C 6F 31 32 33 0D 0A
- decimal：輸入十進位字串（每個 byte 以空白分隔），例如 72 101 108 108 111 49 50 51 13 10
\n請選擇顯示格式後，於傳送欄位輸入對應格式內容再按「傳送」。
www.powenko.com 柯博文老師
""",
    'zh_cn': """
【教学】如何发送数据：
- string：直接输入要发送的文字，例如 Hello123\r\n
- hex：输入十六进制字符串（不分大小写、可有空格），例如 48 65 6C 6C 6F 31 32 33 0D 0A
- decimal：输入十进制字符串（每个字节以空格分隔），例如 72 101 108 108 111 49 50 51 13 10
\n请选择显示格式后，在发送栏输入对应格式内容再按"发送"。
www.powenko.com 柯博文老師
""",
    'es': """
Cómo enviar datos:
- string: Ingrese texto directamente, por ejemplo Hello123\r\n
- hex: Ingrese la cadena hexadecimal (no distingue mayúsculas/minúsculas, espacios permitidos), por ejemplo 48 65 6C 6C 6F 31 32 33 0D 0A
- decimal: Ingrese la cadena decimal (cada byte separado por espacio), por ejemplo 72 101 108 108 111 49 50 51 13 10
\nSeleccione el formato de visualización, ingrese el contenido correspondiente y presione Enviar.
www.powenko.com 柯博文老師
""",
    'pt': """
Como enviar dados:
- string: Digite o texto diretamente, por exemplo Hello123\r\n
- hex: Digite a string hexadecimal (maiúsculas/minúsculas não importam, espaços permitidos), por exemplo 48 65 6C 6C 6F 31 32 33 0D 0A
- decimal: Digite a string decimal (cada byte separado por espaço), por exemplo 72 101 108 108 111 49 50 51 13 10
\nSelecione o formato de exibição, digite o conteúdo correspondente e pressione Enviar.
www.powenko.com 柯博文老師
""",
}

current_lang = 'en'

def get_string(lang, key):
    if lang in STRINGS and key in STRINGS[lang]:
        return STRINGS[lang][key]
    elif 'en' in STRINGS and key in STRINGS['en']:
        return STRINGS['en'][key]
    else:
        return key

def l(key):
    return get_string(current_lang, key)

def read_from_port():
    global ser, stop_thread
    while not stop_thread and ser and ser.is_open:
        try:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                received_data.append(data)
                display_data(data)
            else:
                time.sleep(0.1)
        except Exception as e:
            break

def display_data(data):
    fmt = display_format_cb.get()
    # 處理 ANSI 清屏序列
    if fmt == 'string' and b'\x1b[2J\x1b[;H' in data:
        clear_output()
        # 移除清屏序列再顯示剩餘資料
        data = data.replace(b'\x1b[2J\x1b[;H', b'')
        if not data:
            return
    if fmt == 'string':
        try:
            text = data.decode(errors='replace')
            text = text.replace('\r\n', '\n')
        except:
            text = str(data)
    elif fmt == 'hex':
        # 兩字元一組加空格
        hexstr = binascii.hexlify(data).decode()
        text = ' '.join([hexstr[i:i+2] for i in range(0, len(hexstr), 2)])
    elif fmt == 'decimal':
        # 十進位顯示
        text = ' '.join([str(b) for b in data])
    else:
        text = str(data)
    output_text.insert('end', text)
    output_text.see('end')

def connect():
    global ser, stop_thread, read_thread
    port = com_port_cb.get()
    baud = baudrate_cb.get()
    if not port:
        set_status("請選擇 COM port", "warning")
        return
    try:
        ser = serial.Serial(port, baudrate=int(baud), timeout=0.1)
        stop_thread = False
        read_thread = threading.Thread(target=read_from_port, daemon=True)
        read_thread.start()
        set_status(f"已成功連線到 {port} @ {baud} bps", "info")
    except Exception as e:
        set_status(f"連線失敗: {e}", "error")

def disconnect():
    global ser, stop_thread
    stop_thread = True
    if ser and ser.is_open:
        ser.close()
    set_status("已斷開連線", "info")

def send_data():
    global ser
    if ser and ser.is_open:
        data = send_entry.get()
        fmt = display_format_cb.get()
        if data:
            try:
                if fmt == 'string':
                    ser.write(data.encode())
                elif fmt == 'hex':
                    hex_str = data.replace(' ', '')
                    ser.write(bytes.fromhex(hex_str))
                elif fmt == 'decimal':
                    decs = data.strip().split()
                    ser.write(bytes([int(d) for d in decs]))
                else:
                    ser.write(data.encode())
            except Exception as e:
                set_status(f"傳送失敗: {e}", "error")
    else:
        set_status("尚未連線", "warning")

def clear_output():
    output_text.delete('1.0', 'end')
    received_data.clear()

def save_data():
    fmt = save_format_cb.get()
    filename = f"output.{fmt}"
    try:
        if fmt == 'csv':
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                for d in received_data:
                    writer.writerow([d.decode(errors='replace')])
        else:
            with open(filename, 'w') as f:
                for d in received_data:
                    if display_format_cb.get() == 'string':
                        f.write(d.decode(errors='replace').replace('\r\n', '\n'))
                    elif display_format_cb.get() == 'hex':
                        f.write(binascii.hexlify(d).decode() + '\n')
                    elif display_format_cb.get() == 'decimal':
                        f.write(' '.join([str(b) for b in d]) + '\n')
        set_status(f"已儲存到 {filename}", "info")
    except Exception as e:
        set_status(f"儲存錯誤: {e}", "error")

def set_language(lang):
    global current_lang
    current_lang = lang
    root.title(l('title'))
    # 更新所有 UI 文字
    com_port_label.config(text=l('com_port'))
    reload_btn.config(text=l('reload'))
    baudrate_label.config(text=l('baudrate'))
    connect_btn.config(text=l('connect'))
    disconnect_btn.config(text=l('disconnect'))
    send_label.config(text=l('send_label'))
    send_btn.config(text=l('send'))
    display_format_label.config(text=l('display_format'))
    clear_btn.config(text=l('clear'))
    save_btn.config(text=l('save'))
    save_format_cb.config(values=['csv', 'txt', 'log'])
    save_format_label.config(text=l('save_format'))
    clear_settings_btn.config(text=l('clear_settings'))
    help_menu.entryconfig(0, label=l('teaching'))
    menubar.entryconfig(0, label=l('help'))
    set_status(l('status_ready'), 'info')

def save_setup():
    setup = {
        'com_port': com_port_cb.get(),
        'baudrate': baudrate_cb.get(),
        'display_format': display_format_cb.get(),
        'save_format': save_format_cb.get(),
        'send_text': send_entry.get(),
        'lang': current_lang
    }
    with open(SETUP_FILE, 'w') as f:
        json.dump(setup, f)

def load_setup():
    global current_lang
    if os.path.exists(SETUP_FILE):
        with open(SETUP_FILE, 'r') as f:
            try:
                setup = json.load(f)
                if 'com_port' in setup and setup['com_port'] in com_port_cb['values']:
                    com_port_cb.set(setup['com_port'])
                if 'baudrate' in setup and setup['baudrate'] in baudrate_cb['values']:
                    baudrate_cb.set(setup['baudrate'])
                if 'display_format' in setup and setup['display_format'] in display_format_cb['values']:
                    display_format_cb.set(setup['display_format'])
                if 'save_format' in setup and setup['save_format'] in save_format_cb['values']:
                    save_format_cb.set(setup['save_format'])
                if 'send_text' in setup:
                    send_entry.delete(0, 'end')
                    send_entry.insert(0, setup['send_text'])
                if 'lang' in setup and setup['lang'] in LANGUAGES:
                    current_lang = setup['lang']
            except Exception:
                pass
    set_language(current_lang)
    if com_port_cb.get():
        connect()

def clear_settings():
    com_port_cb.set('')
    baudrate_cb.set('9600')
    display_format_cb.set('string')
    save_format_cb.set('csv')
    send_entry.delete(0, 'end')
    clear_output()
    save_setup()

def on_comport_or_baudrate_change(event=None):
    disconnect()
    connect()
    save_setup()

def on_format_change(event):
    # 不清除舊內容，直接依新格式重顯所有 received_data
    output_text.delete('1.0', 'end')
    for d in received_data:
        display_data(d)

root = tk.Tk()
root.title(l('title'))

# 應用程式選單
menubar = tk.Menu(root)
help_menu = tk.Menu(menubar, tearoff=0)
def show_teaching():
    teach_win = tk.Toplevel(root)
    teach_win.title(l('teaching'))
    teach_win.geometry("500x260")
    text = tk.Text(teach_win, wrap="word", height=12, width=60)
    text.insert("1.0", TEACHING_TEXTS[current_lang])
    text.configure(state="disabled")
    text.pack(expand=True, fill="both", padx=10, pady=10)
    btn = tk.Button(teach_win, text=l('close'), command=teach_win.destroy)
    btn.pack(pady=5)
help_menu.add_command(label=l('teaching'), command=show_teaching)
menubar.add_cascade(label=l('help'), menu=help_menu)

# 語言選單
lang_menu = tk.Menu(menubar, tearoff=0)
def set_lang_and_save(lang):
    set_language(lang)
    save_setup()
lang_menu.add_command(label='English', command=lambda: set_lang_and_save('en'))
lang_menu.add_command(label='繁體中文', command=lambda: set_lang_and_save('zh_tw'))
lang_menu.add_command(label='简体中文', command=lambda: set_lang_and_save('zh_cn'))
lang_menu.add_command(label='Español', command=lambda: set_lang_and_save('es'))
lang_menu.add_command(label='Português', command=lambda: set_lang_and_save('pt'))
menubar.add_cascade(label='Language', menu=lang_menu)
root.config(menu=menubar)

# COM Port 下拉選單
com_port_label = tk.Label(root, text=l('com_port'))
com_port_label.grid(row=0, column=0, padx=5, pady=5)
com_port_cb = ttk.Combobox(root, width=15, state="readonly")
com_port_cb.grid(row=0, column=1, padx=5, pady=5)

# Reload 按鈕
reload_btn = tk.Button(root, text=l('reload'), command=reload_ports)
reload_btn.grid(row=0, column=2, padx=5, pady=5)

# 速度下拉選單
baudrate_label = tk.Label(root, text=l('baudrate'))
baudrate_label.grid(row=0, column=3, padx=5, pady=5)
baudrate_cb = ttk.Combobox(root, width=10, state="readonly")
baudrate_cb['values'] = ['9600', '19200', '38400', '57600', '115200']
baudrate_cb.current(0)
baudrate_cb.grid(row=0, column=4, padx=5, pady=5)

# 連線/斷線按鈕
connect_btn = tk.Button(root, text=l('connect'), command=connect)
connect_btn.grid(row=0, column=5, padx=5, pady=5)
disconnect_btn = tk.Button(root, text=l('disconnect'), command=disconnect)
disconnect_btn.grid(row=0, column=6, padx=5, pady=5)

# 傳送資料
send_label = tk.Label(root, text=l('send_label'))
send_label.grid(row=1, column=0, padx=5, pady=5)
send_entry = tk.Entry(root, width=30)
send_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
send_btn = tk.Button(root, text=l('send'), command=send_data)
send_btn.grid(row=1, column=4, padx=5, pady=5)

# 顯示格式選單
display_format_label = tk.Label(root, text=l('display_format'))
display_format_label.grid(row=1, column=5, padx=5, pady=5)
display_format_cb = ttk.Combobox(root, width=8, state="readonly")
display_format_cb['values'] = ['string', 'hex', 'decimal']
display_format_cb.current(0)
display_format_cb.grid(row=1, column=6, padx=5, pady=5)
display_format_cb.bind('<<ComboboxSelected>>', lambda e: (on_format_change(e), save_setup()))

# 設定 grid 欄列權重，讓 output_text 可自動伸縮
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)
root.grid_columnconfigure(5, weight=1)
root.grid_columnconfigure(6, weight=1)

# 顯示區
output_text = tk.Text(root, height=15, width=80)
output_text.grid(row=2, column=0, columnspan=7, padx=5, pady=5, sticky="nsew")

clear_btn = tk.Button(root, text=l('clear'), command=clear_output)
clear_btn.grid(row=3, column=0, padx=5, pady=5)

save_format_label = tk.Label(root, text=l('save_format'))
save_format_label.grid(row=3, column=1, padx=5, pady=5)
save_format_cb = ttk.Combobox(root, width=6, state="readonly")
save_format_cb['values'] = ['csv', 'txt', 'log']
save_format_cb.current(0)
save_format_cb.grid(row=3, column=2, padx=5, pady=5)
save_btn = tk.Button(root, text=l('save'), command=save_data)
save_btn.grid(row=3, column=3, padx=5, pady=5)

clear_settings_btn = tk.Button(root, text=l('clear_settings'), command=clear_settings)
clear_settings_btn.grid(row=3, column=4, padx=5, pady=5)

# 狀態訊息顯示
status_label = tk.Label(root, text=l('status_ready'), anchor="w", fg="black", bg="#f0f0f0")
status_label.grid(row=4, column=0, columnspan=7, sticky="ew", padx=5, pady=5)

def set_status(msg, msg_type="info"):
    color = {"info": "green", "warning": "orange", "error": "red"}.get(msg_type, "black")
    status_label.config(text=msg, fg=color)

reload_ports()  # 初始化時載入一次
load_setup()    # 載入設定

root.protocol("WM_DELETE_WINDOW", lambda: (disconnect(), root.destroy()))
root.mainloop()
