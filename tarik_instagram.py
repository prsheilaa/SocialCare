import requests

# Masukkan data yang sudah Anda dapatkan
ACCESS_TOKEN = "EAAZAbCoPFcB4BSlivlDfZB3tee3bRD6a5NYTsOf1YFyNdMaLzt7m3RxSVGE2wDPo9jX0toFsKDzeq7IeoGSfaZCTo5UtV7Cn36Tv76B2nAPeouCvMuCAXWXKVI8cf73xZAcME93iOCb7Ir8ENhsz1T2OdbpZAqcXJ7LyCFppvRG8yD4vYuOdHs1bSdLhSB3mndZBFL4JSrv7OjZADFRPadSzHknZAZANHyxFSLbs6ZB8BJcSbhphz1iQccHLUsM2z8thW2jJmO9qOsjSfMnRQZD"
IG_USER_ID = "17841415868144059"

# 1. Mengambil daftar postingan (media) terbaru dari akun Instagram
url_media = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media?fields=id,caption,comments_count,timestamp&access_token={ACCESS_TOKEN}"

response = requests.get(url_media)
data_media = response.json()

print("--- DAFTAR POSTINGAN INSTAGRAM ---")
print(data_media)

# Jika ada postingan, kita bisa ambil ID postingan pertama untuk melihat komentarnya
if 'data' in data_media and len(data_media['data']) > 0:
    first_post_id = data_media['data'][0]['id']
    print(f"\nMengambil komentar dari Post ID: {first_post_id}")

    # 2. Mengambil komentar dari postingan tersebut
    url_comments = f"https://graph.facebook.com/v20.0/{first_post_id}/comments?fields=id,text,username&access_token={ACCESS_TOKEN}"
    
    response_comments = requests.get(url_comments)
    data_comments = response_comments.json()
    
    print("--- KOMENTAR PADA POSTINGAN PERTAMA ---")
    print(data_comments)
else:
    print("Tidak ada postingan ditemukan atau akun belum memiliki media publik.")