# Production Security Checklist

- `SECRET_KEY` باید با secret manager مقداردهی شود و حداقل 64 کاراکتر تصادفی باشد.
- PostgreSQL و Redis نباید مستقیماً روی اینترنت publish شوند.
- TLS باید در reverse proxy فعال شود.
- CORS فقط دامنه‌های واقعی frontend را قبول کند.
- برای SMS، gateway واقعی و rate limit مستقل OTP نصب شود؛ endpoint توسعه‌ای verification در production باید با provider واقعی جایگزین شود.
- callback پرداخت باید signature/reference واقعی gateway را validate کند.
- برای فایل‌های آپلودی، MIME sniffing، size limit، antivirus و object storage جداگانه اعمال شود.
- برای WebSocket/chat، authorization در هر connection و هر room اعمال شود.
- لاگ‌ها نباید password، token، OTP یا داده پرداخت حساس را ثبت کنند.
- backup رمزنگاری‌شده و تست restore دوره‌ای فعال باشد.
