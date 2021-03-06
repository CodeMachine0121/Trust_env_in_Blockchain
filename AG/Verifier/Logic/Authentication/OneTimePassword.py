import pyotp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class otpObject:
    """
        透過 pyotp 產生 OTP，再透過Email轉寄至使用者email
    """

    def __init__(self):
        self.seed = pyotp.random_base32()
        self.optObj = pyotp.TOTP(self.seed, interval=120)

    def sendEmail(self, remoteMail) -> None:
        content = MIMEMultipart()  # 建立MIMEMultipart物件
        content["subject"] = "Trust-Transaction-System Authentication"  # 郵件標題
        content["from"] = "CodeMachine0121@gmail.com"  # 寄件者
        content["to"] = remoteMail  # 收件者
        content.attach(MIMEText("Here's your one-time password: {}".format(self.optObj.now())))  # 郵件內容

        with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
            try:
                smtp.ehlo()  # 驗證SMTP伺服器
                smtp.starttls()  # 建立加密傳輸
                smtp.login("CodeMachine0121@gmail.com", "jsxfjeeobpzxhehw")  # 登入寄件者gmail
                smtp.send_message(content)  # 寄送郵件
                print("\t[-] Send OTP mail to {}".format(remoteMail))
            except Exception as e:
                print("Error message: ", e)

    # one-time-password
    def verify(self, ans: str) -> bool:
        print("[+] OTP Verify Phase:  ")
        print("\t[-] Ans: ", self.optObj.now())
        print("\t[-] Received Ans: ", ans)
        return self.optObj.now() == ans
