const QRCode = require('qrcode');

// النص الذي تريد تحويله إلى QR Code
const textToEncode = 'هذا هو النص الذي تريد تحويله إلى QR Code';

// إنشاء QR Code
QRCode.toDataURL(textToEncode, { errorCorrectionLevel: 'H' }, function (err, url) {
  if (err) {
    console.error(err);
    return;
  }
  console.log(url); // هذا هو رابط الصورة الناتجة
});