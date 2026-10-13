# Desk Robot

Robot để bàn dùng ESP32, dashboard web theo dõi cảm biến và ứng dụng Python trò chuyện với AI cục bộ qua Ollama.

## Thành phần

| File                     | Chức năng                                                             |
| ------------------------ | --------------------------------------------------------------------- |
| `AI_local.PY`            | Giao diện Tkinter, điều khiển UDP, trò chuyện và phân tích môi trường |
| `settings.py`            | Đọc cấu hình Python từ biến môi trường hoặc `.env`                    |
| `robot_cua_tan_phat.ino` | Firmware ESP32, OLED, servo, cảm biến và Pomodoro                     |
| `index.html`             | Dashboard cảm biến, điều khiển robot và quản lý học tập               |
| `login.html`             | Đăng ký/đăng nhập demo với OTP EmailJS                                |
| `emailjs-test.html`      | Kiểm tra gửi email                                                    |

Dashboard và firmware dùng Firebase tại `RobotDashboard/Robots/{robotId}`. Python hiện dùng các node cũ như `ThongSo`, `Task`, `ChatBox` tại gốc database và gửi lệnh UDP đến ESP32. Cần kiểm tra đường dẫn dữ liệu và khả năng nhận UDP của firmware khi ghép các thành phần; việc định dạng không thay đổi giao thức này.

## Cấu hình

| File riêng trên máy | File mẫu được commit | Nội dung                          |
| ------------------- | -------------------- | --------------------------------- |
| `.env`              | `.env.example`       | Địa chỉ ESP32, Firebase và Ollama |
| `config.local.js`   | `config.example.js`  | Firebase Web và EmailJS           |
| `secrets.h`         | `secrets.example.h`  | Wi-Fi và Firebase cho ESP32       |

Khi clone trên máy mới, tạo cấu hình bằng PowerShell:

```powershell
Copy-Item .env.example .env
Copy-Item config.example.js config.local.js
Copy-Item secrets.example.h secrets.h
```

Điền thông tin của bạn vào ba file vừa tạo. Nếu chúng đã tồn tại, hãy sửa trực tiếp để giữ cấu hình hiện tại. Biến môi trường của hệ điều hành được ưu tiên hơn `.env`.

`ROBOT_ID` trong firmware phải trùng với robot được cấp quyền trên dashboard. `DATABASE_URL` trong `secrets.h` cần có dấu `/` ở cuối.

## Chạy Python

Yêu cầu Python 3.10 trở lên có Tkinter và Ollama đang hoạt động.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
```

Mở terminal khác, kích hoạt môi trường ảo và chạy:

```powershell
python AI_local.PY
```

Đổi `OLLAMA_MODEL` trong `.env` nếu dùng model khác. Kiểm tra kết nối mạng, `ESP32_IP` và `ESP32_PORT` trước khi điều khiển robot.

## Chạy dashboard

Sau khi điền `config.local.js`, chạy máy chủ web cục bộ:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Mở `http://127.0.0.1:8000/login.html`. Dùng `emailjs-test.html` để kiểm tra cấu hình EmailJS. Tên tham số OTP phải khớp với template của bạn.

Khi triển khai website, cung cấp cấu hình web qua bước triển khai riêng. Không đưa `.env` hoặc `secrets.h` vào thư mục web công khai.

## Nạp firmware

Mở sketch bằng Arduino IDE với board ESP32, đặt `secrets.h` cạnh file `.ino` và cài các thư viện:

- Adafruit GFX, Adafruit SSD1306, Adafruit AHTX0 và Adafruit BMP280
- BH1750
- ESP32Servo
- Firebase ESP Client

Kiểm tra các chân GPIO trước khi nạp; lấy IP của ESP32 từ Serial Monitor.

## Định dạng code

Cài công cụ Python và Prettier; Prettier cần Node.js 18 trở lên:

```powershell
python -m pip install -r requirements-dev.txt
npm ci
```

Định dạng và kiểm tra:

```powershell
python -m black AI_local.PY settings.py
clang-format -i robot_cua_tan_phat.ino secrets.example.h
npm run format
python -m black --check AI_local.PY settings.py
npm run format:check
```

Quy tắc nằm trong `pyproject.toml`, `.prettierrc.json`, `.clang-format` và `.editorconfig`.

## Đưa lên GitHub

Commit source, file mẫu và `package-lock.json`. `.gitignore` loại cấu hình riêng, môi trường ảo, thư viện tải về và thư mục `.tools`. Nếu thư mục được tải từ ZIP và chưa có Git, chạy `git init` trước.

```powershell
git add .
git diff --cached --name-only
```

Danh sách không được chứa `.env`, `config.local.js`, `secrets.h` hoặc `.tools`. Nếu tải file bằng giao diện GitHub, bạn phải tự loại chúng vì giao diện tải lên không áp dụng `.gitignore`.

Nếu mật khẩu hoặc secret từng được công khai, hãy thay mới chúng; `.gitignore` không xóa dữ liệu khỏi lịch sử commit.

## Giới hạn bảo mật

Cấu hình riêng được giữ khỏi repository. Firebase Web config và EmailJS vẫn có thể xem được trong trình duyệt khi website chạy. Không đặt private key hoặc service account trong JavaScript. Theo [tài liệu Firebase](https://firebase.google.com/docs/projects/api-keys), dữ liệu phải được bảo vệ bằng Security Rules thay vì dựa vào việc giấu Web API key.

`database.rules.json` hiện cho phép đọc/ghi công khai để demo. Luồng đăng nhập kiểm tra mật khẩu và OTP ở phía trình duyệt và lưu mật khẩu trong database. Cần thay bằng Firebase Authentication, Security Rules phù hợp và xác minh OTP ở backend trước khi triển khai công khai.
