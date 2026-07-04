# Robot-Dashboard FIX6

Bản này sửa lỗi EmailJS và sửa thông báo lỗi Firebase PERMISSION_DENIED.

## Chạy project
1. Mở folder bằng VS Code.
2. Bấm phải `login.html` -> Open with Live Server.
3. Bấm Ctrl + F5 để xóa cache.
4. Đăng ký / đăng nhập bằng OTP EmailJS.

## Nếu thấy PERMISSION_DENIED
Lỗi này không phải EmailJS. OTP đã gửi được, nhưng Firebase Realtime Database chưa cho web ghi dữ liệu.

Vào Firebase Console:
Realtime Database -> Rules -> dán nội dung file `database.rules.json` -> Publish.

Rules demo:
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

Chỉ dùng rules này khi demo / học tập. Khi nộp thật nên đổi sang rules có Firebase Authentication.


## Bổ sung MCP Environment Dashboard

Bản `index_mcp.html` đã thêm khu vực **MCP Environment Analysis** trong trang **Giám sát**.

Dashboard đọc dữ liệu MCP tại:

```text
MCP/EnvironmentAnalysis
```

Cấu trúc dữ liệu khuyến nghị:

```json
{
  "source": "python_mcp",
  "environment": {
    "temperature": 28.2,
    "humidity": 56.1,
    "light": 93.3
  },
  "analysis": {
    "temperature_status": "NORMAL",
    "humidity_status": "NORMAL",
    "light_status": "DARK",
    "overall": "NEED_ATTENTION",
    "comfort_score": 90,
    "warnings": ["Ánh sáng đang thấp."],
    "advice": ["Nên bật đèn nếu cần học tập hoặc làm việc."],
    "spoken_summary": "Hiện tại nhiệt độ 28.2°C; độ ẩm 56.1%; ánh sáng 93 lux. Môi trường hiện tại cần chú ý thêm."
  },
  "updated_at": "2026-06-23T18:00:00"
}
```

Nếu Python MCP chưa chạy, dashboard có nút **Phân tích lại từ Dashboard** để tự phân tích tạm từ node `ThongSo` và ghi kết quả lên `MCP/EnvironmentAnalysis`.

Khi dùng với file Python `robot_agent_mcp_full.py`, luồng chuẩn là:

```text
ESP32 -> Firebase/ThongSo -> Python MCP -> Firebase/MCP/EnvironmentAnalysis -> Dashboard
```
