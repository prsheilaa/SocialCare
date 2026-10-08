import requests
import mysql.connector
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Konfigurasi Akun Instagram
ACCESS_TOKEN = "EAAZAbCoPFcB4BSlivlDfZB3tee3bRD6a5NYTsOf1YFyNdMaLzt7m3RxSVGE2wDPo9jX0toFsKDzeq7IeoGSfaZCTo5UtV7Cn36Tv76B2nAPeouCvMuCAXWXKVI8cf73xZAcME93iOCb7Ir8ENhsz1T2OdbpZAqcXJ7LyCFppvRG8yD4vYuOdHs1bSdLhSB3mndZBFL4JSrv7OjZADFRPadSzHknZAZANHyxFSLbs6ZB8BJcSbhphz1iQccHLUsM2z8thW2jJmO9qOsjSfMnRQZD"
IG_USER_ID = "17841415868144059"

# Konfigurasi Database XAMPP MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sosialcare_db"
)
cursor = db.cursor()

# 1. Tarik data postingan
url_media = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media?fields=id,caption&access_token={ACCESS_TOKEN}"
res_media = requests.get(url_media, verify=False).json()

if 'data' in res_media:
    for post in res_media['data']:
        post_id = post.get('id')
        caption = post.get('caption', 'Tanpa Caption')
        
        # 2. Tarik komentar untuk setiap postingan
        url_comments = f"https://graph.facebook.com/v20.0/{post_id}/comments?fields=id,text,username&access_token={ACCESS_TOKEN}"
        res_comments = requests.get(url_comments, verify=False).json()
        comments = res_comments.get('data', [])
        
        # 3. Simpan ke database MySQL
        for comment in comments:
            c_id = comment.get('id')
            username = comment.get('username')
            text = comment.get('text')
            
            # Cek apakah komentar sudah ada agar tidak duplikat
            cursor.execute("SELECT * FROM ig_comments WHERE post_id = %s AND username = %s AND comment_text = %s", (post_id, username, text))
            if cursor.fetchone() is None:
                sql = "INSERT INTO ig_comments (post_id, caption, username, comment_text) VALUES (%s, %s, %s, %s)"
                val = (post_id, caption, username, text)
                cursor.execute(sql, val)
                db.commit()
                print(f"Berhasil menyimpan komentar dari @{username}")

    print("Sinkronisasi data komentar Instagram ke Database XAMPP selesai!")
else:
    print("Tidak ada postingan ditemukan.")

cursor.close()
db.close()