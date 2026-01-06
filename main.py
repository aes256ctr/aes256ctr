import os
import telebot
import instaloader
import glob
import shutil

# 从环境变量获取 Token
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
L = instaloader.Instaloader(download_video_thumbnails=False, save_metadata=False, post_metadata_txt_pattern='')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "你好！发送一个 Instagram 链接给我，我帮你下载视频。")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def download_ig(message):
    url = message.text.strip()
    chat_id = message.chat.id
    
    # 获取 Shortcode (例如 https://www.instagram.com/p/C12345/ -> C12345)
    try:
        shortcode = url.split("/")[-2] if url.endswith('/') else url.split("/")[-1]
        if '?' in shortcode: shortcode = shortcode.split('?')[0]
        
        msg = bot.send_message(chat_id, "正在解析并下载，请稍候...")
        
        # 创建临时文件夹
        target_dir = f"dl_{shortcode}"
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=target_dir)
        
        # 寻找下载好的视频或图片文件
        files = glob.glob(f"{target_dir}/*.mp4") + glob.glob(f"{target_dir}/*.jpg")
        
        for f in files:
            with open(f, 'rb') as video:
                bot.send_document(chat_id, video)
        
        # 清理文件
        shutil.rmtree(target_dir)
        bot.delete_message(chat_id, msg.message_id)
        
    except Exception as e:
        bot.send_message(chat_id, f"下载失败: {str(e)}\n注意：私密账号或被风控的链接无法下载。")

if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling()