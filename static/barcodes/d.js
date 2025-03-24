// qrCode.js

function showBarcode() {
    var barcode = document.getElementById("barcode").innerText; // جلب الباركود من العنصر (تأكد من أنك قد مررت الباركود في HTML)

    if (!barcode) {
        alert("لا يوجد باركود متاح!");  // التنبيه عند عدم وجود باركود
        console.error("الباركود فارغ أو غير موجود!");
        return;
    }

    // عرض الباركود كنص
    document.getElementById("emailText").innerText = "الباركود: " + barcode;

    // حذف أي رمز QR سابق
    document.getElementById("qrcode").innerHTML = "";

    // إنشاء رمز QR باستخدام مكتبة qrcode.js
    QRCode.toCanvas(document.getElementById("qrcode"), barcode, {
        width: 200,   // ضبط حجم QR Code
        height: 200
    }, function(error) {
        if (error) {
            console.error("خطأ في إنشاء الباركود:", error);
        } else {
            console.log("تم إنشاء رمز QR بنجاح!");
        }
    });
}
