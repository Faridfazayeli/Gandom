from dataclasses import dataclass

@dataclass
class Diagnosis:
    title: str
    confidence: float
    risk: str
    steps: list[str]
    safety: list[str]

class RepairAI:
    """Rule-based deterministic core that is safe without a model binary; a model server can be added behind the same interface."""
    def diagnose(self, symptom: str, category: str|None=None) -> Diagnosis:
        s=symptom.lower()
        if any(k in s for k in ["روشن نمی", "خاموش", "no power", "power"]):
            return Diagnosis("مسیر تغذیه و ورودی توان", .82, "high", ["قطع کامل برق و تخلیه خازن‌ها", "بررسی فیوز، کانکتور و مسیر ورودی", "اندازه‌گیری مقاومت ریل تغذیه قبل از تزریق ولتاژ", "بررسی رگولاتور و اتصال کوتاه", "پس از رفع ایراد، تست با محدودکننده جریان"], ["از تزریق مستقیم ولتاژ نامشخص خودداری کنید", "قبل از کار روی خازن‌های ولتاژ بالا تخلیه ایمن انجام دهید"])
        if any(k in s for k in ["داغ", "overheat", "حرارت"]):
            return Diagnosis("بررسی اضافه‌جریان یا اتصال کوتاه", .78, "high", ["قطع تغذیه", "بازرسی حرارتی و چشمی", "اندازه‌گیری مقاومت به زمین", "ایزوله‌کردن شاخه معیوب", "تست تدریجی با محدودکننده جریان"], ["از لمس قطعات داغ خودداری کنید", "برای بردهای برق شهر، جداسازی ایزوله را رعایت کنید"])
        return Diagnosis("عیب‌یابی مرحله‌ای عمومی", .61, "medium", ["ثبت دقیق علائم", "بازرسی چشمی و بررسی سوختگی/لحیم سرد", "اندازه‌گیری تغذیه‌های اصلی", "مقایسه با مقادیر مرجع", "ثبت نتیجه هر تست و حرکت به مرحله بعد"], ["قبل از هر اندازه‌گیری محدوده ابزار را کنترل کنید", "در مدارهای برق شهر فقط با تجهیزات ایمنی مناسب کار کنید"])
