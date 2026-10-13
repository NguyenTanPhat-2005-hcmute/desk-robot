"""Desktop chat and robot controls using Firebase, UDP, and local Ollama."""

import socket
import threading
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, simpledialog

import requests

from settings import (
    ESP32_IP,
    ESP32_PORT,
    FIREBASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_URL,
)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def chay_nen(ham, *args):
    thread = threading.Thread(target=ham, args=args)
    thread.daemon = True
    thread.start()


def lay_thoi_gian():
    return datetime.now().strftime("%H:%M:%S %d/%m/%Y")


def cat_text_oled(text, max_len=90):
    text = str(text).replace("\n", " ").strip()
    if len(text) > max_len:
        text = text[:max_len]
    return text


def firebase_get(path):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
        print("Loi Firebase GET:", res.text)
        return None
    except Exception as e:
        print("Loi doc Firebase:", e)
        return None


def firebase_put(path, data):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        res = requests.put(url, json=data, timeout=5)
        if res.status_code == 200:
            return True
        print("Loi Firebase PUT:", res.text)
        return False
    except Exception as e:
        print("Loi ghi Firebase:", e)
        return False


def firebase_push(path, data):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        res = requests.post(url, json=data, timeout=5)
        if res.status_code == 200:
            return True
        print("Loi Firebase PUSH:", res.text)
        return False
    except Exception as e:
        print("Loi push Firebase:", e)
        return False


def luu_chat_firebase(cau_hoi, cau_tra_loi):
    thoi_gian = lay_thoi_gian()

    firebase_put(
        "ChatBox",
        {
            "CauHoiCuoi": cau_hoi,
            "TraLoiCuoi": cau_tra_loi,
            "TrangThai": "DA_XU_LY",
            "ThoiGian": thoi_gian,
        },
    )

    firebase_push(
        "NhatKy",
        {
            "by": "python_chatbox",
            "icon": "chat",
            "text": f"Nguoi dung: {cau_hoi} | Phan hoi: {cau_tra_loi}",
            "time": thoi_gian,
        },
    )


def luu_lenh_firebase(lenh):
    thoi_gian = lay_thoi_gian()

    firebase_put("ThietBi/LenhCuoiTuChatBox", lenh)

    firebase_push(
        "NhatKy",
        {
            "by": "python_chatbox",
            "icon": "cmd",
            "text": f"Gui lenh UDP sang ESP32: {lenh}",
            "time": thoi_gian,
        },
    )


def gui_udp(lenh):
    try:
        udp_socket.sendto(lenh.encode("utf-8"), (ESP32_IP, ESP32_PORT))
        chay_nen(luu_lenh_firebase, lenh)
        return True
    except Exception as e:
        print("Loi gui UDP:", e)
        return False


def hoi_ollama(cau_hoi, ngu_canh=""):
    try:
        prompt = f"""
Bạn là trợ lý học tập thông minh tích hợp trong robot IoT.

Vai trò:
- Trả lời câu hỏi học tập cho người dùng.
- Phân tích dữ liệu môi trường học tập.
- Đưa ra lời nhắc học tập, sức khỏe và Pomodoro.
- Hỗ trợ quản lý task học tập.

Yêu cầu trả lời:
- Trả lời bằng tiếng Việt.
- Ngắn gọn, rõ ràng, dễ hiểu.
- Không trả lời quá dài.
- Nếu phù hợp, hãy đưa lời khuyên thực tế.
- Không tự nhận mình là ChatGPT, hãy nói là trợ lý AI của robot.

Ngữ cảnh hiện tại:
{ngu_canh}

Câu hỏi của người dùng:
{cau_hoi}
"""

        data = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

        response = requests.post(OLLAMA_URL, json=data, timeout=OLLAMA_TIMEOUT)

        if response.status_code == 200:
            return response.json().get("response", "").strip()
        return f"Ollama đang lỗi hoặc chưa phản hồi. Hãy kiểm tra ollama serve hoặc model {OLLAMA_MODEL}."

    except Exception as e:
        return f"Không kết nối được Ollama: {e}"


def tao_ngu_canh_tu_firebase():
    thong_so = firebase_get("ThongSo")
    task = firebase_get("Task/HienTai")
    goi_y = firebase_get("Task/GoiY")
    pomodoro = firebase_get("Pomodoro")
    thiet_bi = firebase_get("ThietBi")

    lines = []

    if thong_so:
        lines.append("Dữ liệu môi trường:")
        lines.append(f"- Nhiệt độ: {thong_so.get('NhietDo', 0)} °C")
        lines.append(f"- Độ ẩm: {thong_so.get('DoAm', 0)} %")
        lines.append(f"- Ánh sáng: {thong_so.get('AnhSang', 0)} lux")
        lines.append(f"- Áp suất: {thong_so.get('ApSuat', 0)} hPa")
        lines.append(f"- Độ cao: {thong_so.get('DoCao', 0)} m")

    if task:
        lines.append("Task học tập:")
        lines.append(f"- Task hiện tại: {task}")
    if goi_y:
        lines.append(f"- Gợi ý task: {goi_y}")

    if pomodoro:
        lines.append("Pomodoro:")
        lines.append(f"- Đang chạy: {pomodoro.get('DangChay', False)}")
        lines.append(f"- Đang nghỉ: {pomodoro.get('DangNghi', False)}")
        lines.append(f"- Còn lại giây: {pomodoro.get('ConLaiGiay', 0)}")
        lines.append(f"- Vòng: {pomodoro.get('Vong', 1)}")

    if thiet_bi:
        lines.append("Robot:")
        lines.append(f"- Trạng thái: {thiet_bi.get('TrangThai', '')}")
        lines.append(f"- Chế độ: {thiet_bi.get('CheDo', '')}")
        lines.append(f"- Lệnh cuối: {thiet_bi.get('LenhCuoi', '')}")

    return "\n".join(lines)


def xu_ly_hoi_ai(cau_hoi):
    them_tin_nhan("Robot", f"Đang hỏi AI Ollama {OLLAMA_MODEL}...", "system")
    nhan_trang_thai.config(text="Trạng thái: AI đang suy nghĩ...", fg="orange")

    ngu_canh = tao_ngu_canh_tu_firebase()
    cau_tra_loi = hoi_ollama(cau_hoi, ngu_canh)

    them_tin_nhan("AI", cau_tra_loi, "bot")

    tom_tat = cat_text_oled(cau_tra_loi, 90)
    gui_udp("OLED:" + tom_tat)

    chay_nen(luu_chat_firebase, cau_hoi, cau_tra_loi)
    nhan_trang_thai.config(text="Trạng thái: AI đã trả lời", fg="green")


def lay_lenh_robot(cau_hoi):
    cau = cau_hoi.lower()

    if "chào" in cau or "chao" in cau or "xin chào" in cau:
        return "CHAO"

    # Ưu tiên tay trái/phải trước lệnh vẫy tay chung.
    if "tay trái" in cau or "tay trai" in cau:
        return "VAY_TAY_TRAI"

    if "tay phải" in cau or "tay phai" in cau:
        return "VAY_TAY_PHAI"

    if (
        "vẫy hai tay" in cau
        or "vay hai tay" in cau
        or "vẫy tay" in cau
        or "vay tay" in cau
    ):
        return "VAY_HAI_TAY"

    if "lắc đầu" in cau or "lac dau" in cau:
        return "LAC_DAU"

    if (
        "nhìn trái" in cau
        or "nhin trai" in cau
        or "quay đầu trái" in cau
        or "quay dau trai" in cau
    ):
        return "NHIN_TRAI"

    if (
        "nhìn phải" in cau
        or "nhin phai" in cau
        or "quay đầu phải" in cau
        or "quay dau phai" in cau
    ):
        return "NHIN_PHAI"

    if (
        "nhìn thẳng" in cau
        or "nhin thang" in cau
        or "về giữa" in cau
        or "ve giua" in cau
    ):
        return "NHIN_THANG"

    if "dừng học" in cau or "dung hoc" in cau:
        return "DUNG_HOC"

    if "pomodoro" in cau or "bắt đầu học" in cau or "bat dau hoc" in cau:
        return "POMODORO"

    if (
        "môi trường" in cau
        or "moi truong" in cau
        or "nhiệt độ" in cau
        or "nhiet do" in cau
    ):
        return "MOI_TRUONG"

    if "dừng" in cau or "dung" in cau or "stop" in cau:
        return "DUNG"

    return None


def tao_phan_hoi_lenh(lenh):
    bang = {
        "CHAO": "Đã gửi lệnh chào sang robot.",
        "VAY_TAY_TRAI": "Đã gửi lệnh vẫy tay trái sang robot.",
        "VAY_TAY_PHAI": "Đã gửi lệnh vẫy tay phải sang robot.",
        "VAY_HAI_TAY": "Đã gửi lệnh vẫy hai tay sang robot.",
        "LAC_DAU": "Đã gửi lệnh lắc đầu sang robot.",
        "NHIN_TRAI": "Đã gửi lệnh nhìn trái sang robot.",
        "NHIN_PHAI": "Đã gửi lệnh nhìn phải sang robot.",
        "NHIN_THANG": "Đã gửi lệnh nhìn thẳng sang robot.",
        "DUNG": "Đã gửi lệnh dừng, robot về vị trí giữa.",
        "POMODORO": "Đã bật chế độ Pomodoro học tập.",
        "DUNG_HOC": "Đã gửi lệnh dừng Pomodoro.",
        "MOI_TRUONG": "Đã gửi lệnh hiển thị môi trường lên OLED.",
    }
    return bang.get(lenh, "Đã gửi lệnh sang robot.")


def phan_tich_moi_truong_co_ban():
    thong_so = firebase_get("ThongSo")

    if thong_so is None:
        them_tin_nhan("Robot", "Không đọc được dữ liệu môi trường từ Firebase.", "bot")
        return

    nhiet_do = float(thong_so.get("NhietDo", 0))
    do_am = float(thong_so.get("DoAm", 0))
    anh_sang = float(thong_so.get("AnhSang", 0))
    ap_suat = float(thong_so.get("ApSuat", 0))
    do_cao = float(thong_so.get("DoCao", 0))

    nhan_xet = []

    if nhiet_do >= 35:
        nhan_xet.append("nhiệt độ cao, nên tránh học nơi quá nóng")
    elif nhiet_do >= 30:
        nhan_xet.append("hơi nóng, nên bật quạt hoặc ngồi nơi thoáng")
    elif nhiet_do >= 24:
        nhan_xet.append("nhiệt độ khá ổn để học tập")
    else:
        nhan_xet.append("không khí hơi mát")

    if do_am >= 80:
        nhan_xet.append("độ ẩm cao, phòng có thể hơi bí")
    elif do_am >= 50:
        nhan_xet.append("độ ẩm ổn định")
    else:
        nhan_xet.append("độ ẩm thấp, nên uống đủ nước")

    if anh_sang < 100:
        nhan_xet.append("ánh sáng yếu, nên bật thêm đèn học")
    elif anh_sang < 600:
        nhan_xet.append("ánh sáng vừa đủ")
    else:
        nhan_xet.append("ánh sáng mạnh")

    ket_luan = "; ".join(nhan_xet)

    noi_dung = (
        f"Nhiệt độ: {nhiet_do:.1f} °C\n"
        f"Độ ẩm: {do_am:.1f} %\n"
        f"Ánh sáng: {anh_sang:.1f} lux\n"
        f"Áp suất: {ap_suat:.1f} hPa\n"
        f"Độ cao: {do_cao:.1f} m\n"
        f"Nhận xét: {ket_luan}"
    )

    oled = f"{nhiet_do:.1f}C {do_am:.0f}% - {nhan_xet[0]}"
    gui_udp("OLED:" + cat_text_oled(oled, 90))

    them_tin_nhan("Robot", noi_dung, "bot")
    chay_nen(luu_chat_firebase, "Phân tích môi trường", noi_dung)
    nhan_trang_thai.config(text="Trạng thái: Đã phân tích môi trường", fg="green")


def ai_phan_tich_moi_truong():
    cau_hoi = "Hãy phân tích điều kiện môi trường hiện tại và đưa lời khuyên học tập, sức khỏe ngắn gọn."
    xu_ly_hoi_ai(cau_hoi)


def them_task():
    task = simpledialog.askstring("Thêm task", "Nhập task học tập:")
    if not task:
        return

    goi_y = simpledialog.askstring("Gợi ý", "Nhập gợi ý ngắn cho task:")
    if not goi_y:
        goi_y = "Tập trung hoàn thành task này."

    firebase_put("Task/HienTai", task)
    firebase_put("Task/GoiY", goi_y)

    firebase_push(
        "NhatKy",
        {
            "by": "python_chatbox",
            "icon": "task",
            "text": f"Them task: {task} | Goi y: {goi_y}",
            "time": lay_thoi_gian(),
        },
    )

    gui_udp("OLED:Task moi: " + cat_text_oled(task, 70))
    them_tin_nhan("Robot", f"Đã thêm task:\n{task}\nGợi ý: {goi_y}", "bot")


def xem_task():
    task = firebase_get("Task/HienTai")
    goi_y = firebase_get("Task/GoiY")

    if task is None:
        task = "Chưa có task."
    if goi_y is None:
        goi_y = "Chưa có gợi ý."

    noi_dung = f"Task hiện tại: {task}\nGợi ý: {goi_y}"
    them_tin_nhan("Robot", noi_dung, "bot")
    gui_udp("OLED:" + cat_text_oled(task, 80))


def ai_phan_tich_task():
    task = firebase_get("Task/HienTai")
    if task is None:
        them_tin_nhan("Robot", "Chưa có task để AI phân tích.", "bot")
        return

    cau_hoi = (
        f"Hãy phân tích task học tập này và đưa kế hoạch ngắn gọn theo Pomodoro: {task}"
    )
    xu_ly_hoi_ai(cau_hoi)


def them_tin_nhan(nguoi_gui, noi_dung, tag):
    thoi_gian = datetime.now().strftime("%H:%M:%S")
    khung_chat.config(state=tk.NORMAL)
    khung_chat.insert(tk.END, f"[{thoi_gian}] {nguoi_gui}: {noi_dung}\n\n", tag)
    khung_chat.config(state=tk.DISABLED)
    khung_chat.yview(tk.END)


def gui_tin_nhan():
    cau_hoi = o_nhap.get().strip()
    if cau_hoi == "":
        return

    o_nhap.delete(0, tk.END)
    them_tin_nhan("Bạn", cau_hoi, "user")

    cau_lower = cau_hoi.lower()

    if "phân tích môi trường" in cau_lower or "phan tich moi truong" in cau_lower:
        them_tin_nhan("Robot", "Đang đọc dữ liệu môi trường từ Firebase...", "system")
        chay_nen(phan_tich_moi_truong_co_ban)
        return

    if "ai môi trường" in cau_lower or "ai moi truong" in cau_lower:
        chay_nen(ai_phan_tich_moi_truong)
        return

    if "thêm task" in cau_lower or "them task" in cau_lower:
        them_task()
        return

    if "xem task" in cau_lower:
        chay_nen(xem_task)
        return

    if (
        "ai task" in cau_lower
        or "phân tích task" in cau_lower
        or "phan tich task" in cau_lower
    ):
        chay_nen(ai_phan_tich_task)
        return

    lenh = lay_lenh_robot(cau_hoi)

    if lenh:
        ok = gui_udp(lenh)
        phan_hoi = tao_phan_hoi_lenh(lenh)

        if ok:
            phan_hoi += f"\nLệnh UDP: {lenh}"
            nhan_trang_thai.config(text=f"Trạng thái: Đã gửi {lenh}", fg="green")
        else:
            phan_hoi += "\nKhông gửi được lệnh sang ESP32."
            nhan_trang_thai.config(text="Trạng thái: Lỗi UDP", fg="red")

        them_tin_nhan("Robot", phan_hoi, "bot")
        chay_nen(luu_chat_firebase, cau_hoi, phan_hoi)
        return

    chay_nen(xu_ly_hoi_ai, cau_hoi)


def nut_gui_lenh(lenh):
    ok = gui_udp(lenh)

    if ok:
        noi_dung = f"Đã gửi lệnh nhanh: {lenh}"
        them_tin_nhan("Robot", noi_dung, "system")
        nhan_trang_thai.config(text=f"Trạng thái: Đã gửi {lenh}", fg="green")
        chay_nen(luu_chat_firebase, "Nút nhanh: " + lenh, noi_dung)
    else:
        them_tin_nhan("Robot", f"Lỗi gửi lệnh: {lenh}", "system")
        nhan_trang_thai.config(text="Trạng thái: Lỗi gửi UDP", fg="red")


def gui_oled_tu_nhap():
    text = simpledialog.askstring("Gửi OLED", "Nhập nội dung muốn hiện lên OLED:")
    if not text:
        return
    nut_gui_lenh("OLED:" + cat_text_oled(text, 90))


def xoa_chat():
    khung_chat.config(state=tk.NORMAL)
    khung_chat.delete(1.0, tk.END)
    khung_chat.config(state=tk.DISABLED)
    nhan_trang_thai.config(text="Trạng thái: Đã xóa chat", fg="black")


def cap_nhat_ip():
    global ESP32_IP
    ip_moi = simpledialog.askstring(
        "Sửa IP ESP32", "Nhập IP ESP32:", initialvalue=ESP32_IP
    )
    if ip_moi:
        ESP32_IP = ip_moi.strip()
        nhan_ip.config(text=f"ESP32 IP: {ESP32_IP}:{ESP32_PORT}")
        them_tin_nhan("System", f"Đã cập nhật IP ESP32: {ESP32_IP}", "system")


def test_ollama():
    chay_nen(xu_ly_hoi_ai, "Bạn đang hoạt động không? Hãy trả lời một câu ngắn.")


def main():
    global app, khung_chat, nhan_ip, nhan_trang_thai, o_nhap

    app = tk.Tk()
    app.title(f"Node Máy Tính - Robot Chat Box + Ollama {OLLAMA_MODEL}")
    app.geometry("960x760")
    app.configure(bg="#f2f2f2")

    tieu_de = tk.Label(
        app,
        text=f"NODE MÁY TÍNH - ROBOT CHAT BOX + OLLAMA {OLLAMA_MODEL}",
        font=("Arial", 16, "bold"),
        bg="#f2f2f2",
    )
    tieu_de.pack(pady=8)

    nhan_ip = tk.Label(
        app,
        text=f"ESP32 IP: {ESP32_IP}:{ESP32_PORT} | Firebase: đã cấu hình | Ollama: {OLLAMA_MODEL}",
        font=("Arial", 10),
        bg="#f2f2f2",
    )
    nhan_ip.pack()

    nhan_trang_thai = tk.Label(
        app, text="Trạng thái: Sẵn sàng", font=("Arial", 11), bg="#f2f2f2"
    )
    nhan_trang_thai.pack(pady=3)

    khung_chat = scrolledtext.ScrolledText(
        app, wrap=tk.WORD, width=112, height=22, font=("Arial", 11)
    )
    khung_chat.pack(padx=10, pady=8)
    khung_chat.config(state=tk.DISABLED)

    khung_chat.tag_config("user", foreground="blue")
    khung_chat.tag_config("bot", foreground="green")
    khung_chat.tag_config("system", foreground="purple")

    khung_nhap = tk.Frame(app, bg="#f2f2f2")
    khung_nhap.pack(pady=5)

    o_nhap = tk.Entry(khung_nhap, width=82, font=("Arial", 12))
    o_nhap.grid(row=0, column=0, padx=5)

    tk.Button(khung_nhap, text="Gửi", width=12, command=gui_tin_nhan).grid(
        row=0, column=1, padx=5
    )
    tk.Button(khung_nhap, text="Xóa chat", width=12, command=xoa_chat).grid(
        row=0, column=2, padx=5
    )
    tk.Button(khung_nhap, text="Sửa IP", width=12, command=cap_nhat_ip).grid(
        row=0, column=3, padx=5
    )

    o_nhap.bind("<Return>", lambda event: gui_tin_nhan())

    khung_nut = tk.LabelFrame(
        app, text="Điều khiển robot", bg="#f2f2f2", font=("Arial", 11, "bold")
    )
    khung_nut.pack(padx=10, pady=7, fill="x")

    cac_nut = [
        ("Chào", "CHAO"),
        ("Vẫy tay trái", "VAY_TAY_TRAI"),
        ("Vẫy tay phải", "VAY_TAY_PHAI"),
        ("Vẫy hai tay", "VAY_HAI_TAY"),
        ("Lắc đầu", "LAC_DAU"),
        ("Nhìn trái", "NHIN_TRAI"),
        ("Nhìn phải", "NHIN_PHAI"),
        ("Nhìn thẳng", "NHIN_THANG"),
        ("Pomodoro", "POMODORO"),
        ("Dừng học", "DUNG_HOC"),
        ("Môi trường", "MOI_TRUONG"),
        ("Dừng", "DUNG"),
    ]

    for i, (ten, lenh) in enumerate(cac_nut):
        tk.Button(
            khung_nut, text=ten, width=17, command=lambda l=lenh: nut_gui_lenh(l)
        ).grid(row=i // 6, column=i % 6, padx=5, pady=5)

    khung_ai = tk.LabelFrame(
        app,
        text="AI Ollama / Task / Môi trường",
        bg="#f2f2f2",
        font=("Arial", 11, "bold"),
    )
    khung_ai.pack(padx=10, pady=5, fill="x")

    tk.Button(khung_ai, text="Test Ollama", width=20, command=test_ollama).grid(
        row=0, column=0, padx=5, pady=5
    )
    tk.Button(
        khung_ai,
        text="Phân tích môi trường",
        width=20,
        command=lambda: chay_nen(phan_tich_moi_truong_co_ban),
    ).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(
        khung_ai,
        text="AI môi trường",
        width=20,
        command=lambda: chay_nen(ai_phan_tich_moi_truong),
    ).grid(row=0, column=2, padx=5, pady=5)
    tk.Button(khung_ai, text="Thêm task", width=20, command=them_task).grid(
        row=0, column=3, padx=5, pady=5
    )
    tk.Button(
        khung_ai, text="Xem task", width=20, command=lambda: chay_nen(xem_task)
    ).grid(row=0, column=4, padx=5, pady=5)
    tk.Button(
        khung_ai, text="AI task", width=20, command=lambda: chay_nen(ai_phan_tich_task)
    ).grid(row=0, column=5, padx=5, pady=5)

    khung_bieu_cam = tk.LabelFrame(
        app, text="Biểu cảm OLED", bg="#f2f2f2", font=("Arial", 11, "bold")
    )
    khung_bieu_cam.pack(padx=10, pady=5, fill="x")

    tk.Button(
        khung_bieu_cam,
        text="Mắt trái",
        width=15,
        command=lambda: nut_gui_lenh("EMOTION:TRAI"),
    ).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(
        khung_bieu_cam,
        text="Mắt phải",
        width=15,
        command=lambda: nut_gui_lenh("EMOTION:PHAI"),
    ).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(
        khung_bieu_cam,
        text="Nhìn lên",
        width=15,
        command=lambda: nut_gui_lenh("EMOTION:LEN"),
    ).grid(row=0, column=2, padx=5, pady=5)
    tk.Button(
        khung_bieu_cam,
        text="Mắt nhắm",
        width=15,
        command=lambda: nut_gui_lenh("EMOTION:NHAM"),
    ).grid(row=0, column=3, padx=5, pady=5)
    tk.Button(
        khung_bieu_cam,
        text="Mặt vui",
        width=15,
        command=lambda: nut_gui_lenh("EMOTION:VUI"),
    ).grid(row=0, column=4, padx=5, pady=5)
    tk.Button(khung_bieu_cam, text="Gửi OLED", width=15, command=gui_oled_tu_nhap).grid(
        row=0, column=5, padx=5, pady=5
    )

    them_tin_nhan(
        "Robot",
        "Xin chào! Bạn có thể nhập: chào, vẫy tay, lắc đầu, nhìn trái, phân tích môi trường, AI môi trường, thêm task, xem task, AI task hoặc hỏi kiến thức bất kỳ để Ollama trả lời.",
        "bot",
    )

    app.mainloop()


if __name__ == "__main__":
    main()
