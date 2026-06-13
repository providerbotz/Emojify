from telegram import Update, ChatMember, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import logging
import re
import json
import os
import requests
import random
from datetime import datetime
import asyncio

# ---------- HELPER: Strip emojis from button text ----------
def strip_emojis(text: str) -> str:
    """Button text se saare emoji characters hata do"""
    emoji_pattern = re.compile(
        r'['
        r'\U0001F1E6-\U0001F1FF\U0001F600-\U0001F64F\U0001F300-\U0001F5FF'
        r'\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF'
        r'\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF'
        r'\u2600-\u26FF\u2700-\u27BF\u2300-\u23FF\uFE0F\u200D'
        r']+',
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text).strip()
# -----------------------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "BOT-TOKEN"
EMOJI_FILE = "emojis.json"

# Fallback emojis list for when no match found
FALLBACK_EMOJIS_LIST = [
    "verified", "blue_verification", "bottle", "heart", "stars", 
    "diamond", "crown", "gift", "fire", "rocket", "smile", 
    "thumbs", "skull", "teddy", "devil", "crying", "flex"
]

PREMIUM_EMOJIS = {
    "verified": {"id": "6147565374289220368", "fallback": "✅", "added_by": "system", "date": "2024-01-01"},
    "flex": {"id": "6147464060305676048", "fallback": "😎", "added_by": "system", "date": "2024-01-01"},
    "blue_verification": {"id": "6147524086768604985", "fallback": "💎", "added_by": "system", "date": "2024-01-01"},
    "frozen": {"id": "5449449325434266744", "fallback": "❄️", "added_by": "system", "date": "2024-01-01"},
    "crying": {"id": "6273840152980755328", "fallback": "😭", "added_by": "system", "date": "2024-01-01"},
    "smiling": {"id": "6276057176444246654", "fallback": "🙂", "added_by": "system", "date": "2024-01-01"},
    "seeing_up": {"id": "6273997026661241933", "fallback": "😋", "added_by": "system", "date": "2024-01-01"},
    "teeth": {"id": "6273726078649372769", "fallback": "😁", "added_by": "system", "date": "2024-01-01"},
    "done": {"id": "6274007313107915274", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "blue_badge": {"id": "5978776771623914876", "fallback": "🟫", "added_by": "system", "date": "2024-01-01"},
    "black_badge": {"id": "5978686323907628843", "fallback": "🔸", "added_by": "system", "date": "2024-01-01"},
    "busy_tag": {"id": "5852873584912896283", "fallback": "🟧", "added_by": "system", "date": "2024-01-01"},
    "instagram": {"id": "5895297528106061174", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "telegram": {"id": "5895735846698487922", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "whatsapp": {"id": "5895343514320899727", "fallback": "🌐", "added_by": "system", "date": "2024-01-01"},
    "india": {"id": "5913754823643107921", "fallback": "🇮🇳", "added_by": "system", "date": "2024-01-01"},
    "dollar": {"id": "5197434882321567830", "fallback": "💵", "added_by": "system", "date": "2024-01-01"},
    "top": {"id": "5463071033256848094", "fallback": "🔝", "added_by": "system", "date": "2024-01-01"},
    "bro": {"id": "5463256910851546817", "fallback": "🤝", "added_by": "system", "date": "2024-01-01"},
    "yes": {"id": "5463423955014529788", "fallback": "👌", "added_by": "system", "date": "2024-01-01"},
    "lock": {"id": "5465443379917629504", "fallback": "🔓", "added_by": "system", "date": "2024-01-01"},
    "good": {"id": "5465465194056525619", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "sigma": {"id": "6235620067942341623", "fallback": "🥃", "added_by": "system", "date": "2024-01-01"},
    "don": {"id": "6235717714023814969", "fallback": "🍂", "added_by": "system", "date": "2024-01-01"},
    "skills": {"id": "6235593671073339928", "fallback": "💀", "added_by": "system", "date": "2024-01-01"},
    "heart": {"id": "6147617184479711380", "fallback": "❤️‍🔥", "added_by": "system", "date": "2024-01-01"},
    "stars": {"id": "6235403472741603087", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "github": {"id": "5346181118884331907", "fallback": "📱", "added_by": "system", "date": "2024-01-01"},
    "motion": {"id": "5971944878815317190", "fallback": "💠", "added_by": "system", "date": "2024-01-01"},
    "bottle": {"id": "6129399728506412489", "fallback": "🍼", "added_by": "system", "date": "2024-01-01"},
    "check": {"id": "6129812419028982717", "fallback": "✅", "added_by": "system", "date": "2024-01-01"},
    "cry": {"id": "6129574787078429498", "fallback": "😪", "added_by": "system", "date": "2024-01-01"},
    "exclaim": {"id": "6129477982810545152", "fallback": "‼️", "added_by": "system", "date": "2024-01-01"},
    "nerd": {"id": "6129550284290006595", "fallback": "🧐", "added_by": "system", "date": "2024-01-01"},
    "sparkle": {"id": "6129479035077531636", "fallback": "✨", "added_by": "system", "date": "2024-01-01"},
    "heartfire": {"id": "6129932613688764241", "fallback": "❤️‍🔥", "added_by": "system", "date": "2024-01-01"},
    "white_heart": {"id": "6129444065453808638", "fallback": "🤍", "added_by": "system", "date": "2024-01-01"},
    "tick": {"id": "6129828611055689014", "fallback": "✔️", "added_by": "system", "date": "2024-01-01"},
    "check2": {"id": "6129472184604695207", "fallback": "✅", "added_by": "system", "date": "2024-01-01"},
    "diamond": {"id": "6129760505759276442", "fallback": "💠", "added_by": "system", "date": "2024-01-01"},
    "teddy": {"id": "6129959208126258284", "fallback": "🧸", "added_by": "system", "date": "2024-01-01"},
    "thumbs": {"id": "6129705667616841573", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "megaphone": {"id": "6129433877791382400", "fallback": "📣", "added_by": "system", "date": "2024-01-01"},
    "crown": {"id": "6129705083501293112", "fallback": "👑", "added_by": "system", "date": "2024-01-01"},
    "gift": {"id": "6131660826924292492", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "gift2": {"id": "6129727043669072880", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "gift3": {"id": "6129415619885407680", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "star": {"id": "6129909635613726974", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "top2": {"id": "6129627894349045589", "fallback": "🔝", "added_by": "system", "date": "2024-01-01"},
    "gift4": {"id": "6129870783339567154", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "calendar": {"id": "6129779562529168023", "fallback": "🗓", "added_by": "system", "date": "2024-01-01"},
    "smile": {"id": "6129772480128097710", "fallback": "😊", "added_by": "system", "date": "2024-01-01"},
    "thought": {"id": "6129939837823753679", "fallback": "💭", "added_by": "system", "date": "2024-01-01"},
    "pin": {"id": "6129694470637100146", "fallback": "📌", "added_by": "system", "date": "2024-01-01"},
    "pin2": {"id": "6129434968713076807", "fallback": "📌", "added_by": "system", "date": "2024-01-01"},
    "money": {"id": "6129732880529628243", "fallback": "💵", "added_by": "system", "date": "2024-01-01"},
    "up": {"id": "6129570565125577536", "fallback": "🔼", "added_by": "system", "date": "2024-01-01"},
    "warning": {"id": "6129782440157256336", "fallback": "⚠️", "added_by": "system", "date": "2024-01-01"},
    "money2": {"id": "6129731974291527294", "fallback": "💸", "added_by": "system", "date": "2024-01-01"},
    "boom": {"id": "6129532314146838421", "fallback": "💥", "added_by": "system", "date": "2024-01-01"},
    "bolt": {"id": "6129805465476929485", "fallback": "⚡", "added_by": "system", "date": "2024-01-01"},
    "hat": {"id": "6129650399977675538", "fallback": "🎩", "added_by": "system", "date": "2024-01-01"},
    "chart": {"id": "6129801569941592173", "fallback": "📊", "added_by": "system", "date": "2024-01-01"},
    "gift5": {"id": "6129769198773083022", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "heart2": {"id": "6129708236007283169", "fallback": "❤️", "added_by": "system", "date": "2024-01-01"},
    "lock2": {"id": "6129906126625447892", "fallback": "🔒", "added_by": "system", "date": "2024-01-01"},
    "crown2": {"id": "6129553312241949602", "fallback": "👑", "added_by": "system", "date": "2024-01-01"},
    "thumbs2": {"id": "6129494286506401122", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "crown3": {"id": "6129778965528713511", "fallback": "👑", "added_by": "system", "date": "2024-01-01"},
    "star2": {"id": "6129915811776698328", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "skull": {"id": "6132184924603554220", "fallback": "💀", "added_by": "system", "date": "2024-01-01"},
    "starstruck": {"id": "6129572317472233948", "fallback": "🤩", "added_by": "system", "date": "2024-01-01"},
    "heart3": {"id": "6129950489342647259", "fallback": "💟", "added_by": "system", "date": "2024-01-01"},
    "pin3": {"id": "6131886699254388574", "fallback": "📌", "added_by": "system", "date": "2024-01-01"},
    "speaker": {"id": "6129492160497589882", "fallback": "🔈", "added_by": "system", "date": "2024-01-01"},
    "angel": {"id": "6129518870899203008", "fallback": "👼", "added_by": "system", "date": "2024-01-01"},
    "devil": {"id": "6129522839448984992", "fallback": "😈", "added_by": "system", "date": "2024-01-01"},
    "wink": {"id": "6129903231817488942", "fallback": "😉", "added_by": "system", "date": "2024-01-01"},
    "check3": {"id": "6129814111246097614", "fallback": "✅", "added_by": "system", "date": "2024-01-01"},
    "car": {"id": "6129643455015557847", "fallback": "🚘", "added_by": "system", "date": "2024-01-01"},
    "diamond2": {"id": "6129736819014639296", "fallback": "🔸", "added_by": "system", "date": "2024-01-01"},
    "sob": {"id": "6129622134797900004", "fallback": "😭", "added_by": "system", "date": "2024-01-01"},
    "star3": {"id": "6129704267457501209", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "star4": {"id": "6129653943325694007", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "star5": {"id": "6132019972089585518", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "glow": {"id": "6129405805885135490", "fallback": "💫", "added_by": "system", "date": "2024-01-01"},
    "rocket": {"id": "6129639980387015660", "fallback": "🚀", "added_by": "system", "date": "2024-01-01"},
    "teddy2": {"id": "6129650743575060215", "fallback": "🧸", "added_by": "system", "date": "2024-01-01"},
    "bolt2": {"id": "6129817830687775854", "fallback": "⚡", "added_by": "system", "date": "2024-01-01"},
    "glow2": {"id": "6129812371784342357", "fallback": "💫", "added_by": "system", "date": "2024-01-01"},
    "star6": {"id": "6129546277085520554", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "star7": {"id": "6129700535130922338", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "calendar2": {"id": "6129771638314523716", "fallback": "🗓", "added_by": "system", "date": "2024-01-01"},
    "boom2": {"id": "6129780730760273719", "fallback": "💥", "added_by": "system", "date": "2024-01-01"},
    "money_mouth": {"id": "6129488844782836766", "fallback": "🤑", "added_by": "system", "date": "2024-01-01"},
    "star8": {"id": "6129672630728400259", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "fire": {"id": "6129792056589031358", "fallback": "🔥", "added_by": "system", "date": "2024-01-01"},
    "champagne": {"id": "6129432683790473996", "fallback": "🍾", "added_by": "system", "date": "2024-01-01"},
    "party": {"id": "6129579803600231171", "fallback": "🎉", "added_by": "system", "date": "2024-01-01"},
    "star9": {"id": "6129692490657175257", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "star10": {"id": "6129542888356321971", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "star11": {"id": "6129566600870764865", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "star12": {"id": "6129846551134084367", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "gift6": {"id": "6129497211379129336", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "flag": {"id": "6129499663805456653", "fallback": "🚩", "added_by": "system", "date": "2024-01-01"},
    "email": {"id": "6129432481927010933", "fallback": "✉️", "added_by": "system", "date": "2024-01-01"},
    "crown4": {"id": "6129635212973316679", "fallback": "👑", "added_by": "system", "date": "2024-01-01"},
    "tongue": {"id": "6132195782280879053", "fallback": "😛", "added_by": "system", "date": "2024-01-01"},
    "relieved": {"id": "6129873716802231439", "fallback": "😌", "added_by": "system", "date": "2024-01-01"},
    "indian": {"id": "6129712921816604452", "fallback": "🇮🇳", "added_by": "system", "date": "2024-01-01"},
    "earth": {"id": "6129903927602190764", "fallback": "🌎", "added_by": "system", "date": "2024-01-01"},
    "card": {"id": "6129926111108275647", "fallback": "💳", "added_by": "system", "date": "2024-01-01"},
    "money3": {"id": "6129680679497111287", "fallback": "💸", "added_by": "system", "date": "2024-01-01"},
    "top3": {"id": "6129704739903906195", "fallback": "🔝", "added_by": "system", "date": "2024-01-01"},
    "indian2": {"id": "6129782715035163979", "fallback": "🇮🇳", "added_by": "system", "date": "2024-01-01"},
    "indian3": {"id": "6129630071897462884", "fallback": "🇮🇳", "added_by": "system", "date": "2024-01-01"},
    "cry2": {"id": "6129704885932794253", "fallback": "😭", "added_by": "system", "date": "2024-01-01"},
    "shocked": {"id": "6129888444245089008", "fallback": "😯", "added_by": "system", "date": "2024-01-01"},
    "skull2": {"id": "6129889801454754893", "fallback": "☠️", "added_by": "system", "date": "2024-01-01"},
    "check4": {"id": "6129891098534877664", "fallback": "✅", "added_by": "system", "date": "2024-01-01"},
    "cat": {"id": "6129625171339778354", "fallback": "🐈‍⬛", "added_by": "system", "date": "2024-01-01"},
    "gift7": {"id": "6129650777934798600", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "white": {"id": "6129780378572954907", "fallback": "⬜️", "added_by": "system", "date": "2024-01-01"},
    "eyes": {"id": "6129879029676776924", "fallback": "👀", "added_by": "system", "date": "2024-01-01"},
    "gift8": {"id": "6129782839589214594", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "heartfire2": {"id": "6129616057419175458", "fallback": "❤️‍🔥", "added_by": "system", "date": "2024-01-01"},
    "bell": {"id": "6129577213734952104", "fallback": "🔔", "added_by": "system", "date": "2024-01-01"},
    "skull3": {"id": "6129631914438434952", "fallback": "💀", "added_by": "system", "date": "2024-01-01"},
    "diamond3": {"id": "6129509499280563691", "fallback": "💎", "added_by": "system", "date": "2024-01-01"},
    "disguise": {"id": "6129781254746282923", "fallback": "🥸", "added_by": "system", "date": "2024-01-01"},
    "star101": {"id": "6129455898088709012", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "moai": {"id": "6129776848109836451", "fallback": "🗿", "added_by": "system", "date": "2024-01-01"},
    "xmas": {"id": "6129470861754771141", "fallback": "🎄", "added_by": "system", "date": "2024-01-01"},
    "blue_heart": {"id": "6129736771769997767", "fallback": "💙", "added_by": "system", "date": "2024-01-01"},
    "link": {"id": "6129589862413638401", "fallback": "🔗", "added_by": "system", "date": "2024-01-01"},
    "thumbs_up": {"id": "6129872028880083998", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "block": {"id": "6129840374971112593", "fallback": "🚫", "added_by": "system", "date": "2024-01-01"},
    "check_mark": {"id": "6129776315533893189", "fallback": "✔️", "added_by": "system", "date": "2024-01-01"},
    "gem": {"id": "6129410405795110009", "fallback": "💎", "added_by": "system", "date": "2024-01-01"},
    "bubble": {"id": "6129579597441801084", "fallback": "💬", "added_by": "system", "date": "2024-01-01"},
    "heart_fire": {"id": "6129913724422593277", "fallback": "❤️‍🔥", "added_by": "system", "date": "2024-01-01"},
    "ribbon": {"id": "6129668331466135693", "fallback": "🎀", "added_by": "system", "date": "2024-01-01"},
    "bookmark": {"id": "6129746001654718223", "fallback": "🔖", "added_by": "system", "date": "2024-01-01"},
    "bag": {"id": "6129574671114313022", "fallback": "🛍", "added_by": "system", "date": "2024-01-01"},
    "bell2": {"id": "6129652186684070216", "fallback": "🔔", "added_by": "system", "date": "2024-01-01"},
    "storm": {"id": "6129769130053605799", "fallback": "🌩", "added_by": "system", "date": "2024-01-01"},
    "gift_heart": {"id": "6129895818703936830", "fallback": "💝", "added_by": "system", "date": "2024-01-01"},
    "hearts": {"id": "6129476453802188018", "fallback": "💕", "added_by": "system", "date": "2024-01-01"},
    "ghost": {"id": "6129758830722030858", "fallback": "👻", "added_by": "system", "date": "2024-01-01"},
    "heart_arrow": {"id": "6129602914819250817", "fallback": "💘", "added_by": "system", "date": "2024-01-01"},
    "slider": {"id": "6129544215501216365", "fallback": "🎚", "added_by": "system", "date": "2024-01-01"},
    "alarm": {"id": "6129532640564354033", "fallback": "🚨", "added_by": "system", "date": "2024-01-01"},
    "gift9": {"id": "6129520790749584124", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "pleading": {"id": "6129517792862413944", "fallback": "🥹", "added_by": "system", "date": "2024-01-01"},
    "smile2": {"id": "6129863473305230077", "fallback": "😊", "added_by": "system", "date": "2024-01-01"},
    "slight_smile": {"id": "6129440444796378483", "fallback": "🙂", "added_by": "system", "date": "2024-01-01"},
    "thumbs3": {"id": "6129443429798648428", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "smile3": {"id": "6129521443584612989", "fallback": "😊", "added_by": "system", "date": "2024-01-01"},
    "angry": {"id": "6129593109408913890", "fallback": "😠", "added_by": "system", "date": "2024-01-01"},
    "unamused": {"id": "6129553763213515073", "fallback": "😒", "added_by": "system", "date": "2024-01-01"},
    "point_up": {"id": "6129523887421006760", "fallback": "👆", "added_by": "system", "date": "2024-01-01"},
    "cursing": {"id": "6129530544620314433", "fallback": "🤬", "added_by": "system", "date": "2024-01-01"},
    "exclaim2": {"id": "6129610250623393142", "fallback": "‼️", "added_by": "system", "date": "2024-01-01"},
    "joy": {"id": "6129600178925083831", "fallback": "😂", "added_by": "system", "date": "2024-01-01"},
    "star13": {"id": "6129418755211533815", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "blue_heart2": {"id": "6129700689749744824", "fallback": "💙", "added_by": "system", "date": "2024-01-01"},
    "star14": {"id": "6129672231296440969", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "gift10": {"id": "6129741083917162817", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "apple": {"id": "6129741453284350735", "fallback": "🍏", "added_by": "system", "date": "2024-01-01"},
    "angel2": {"id": "6129700595260463994", "fallback": "👼", "added_by": "system", "date": "2024-01-01"},
    "devil2": {"id": "6129766986864924223", "fallback": "😈", "added_by": "system", "date": "2024-01-01"},
    "star15": {"id": "6129421254882500490", "fallback": "⭐", "added_by": "system", "date": "2024-01-01"},
    "lock3": {"id": "6129731845442510016", "fallback": "🔐", "added_by": "system", "date": "2024-01-01"},
    "ring": {"id": "6129913342170506824", "fallback": "💍", "added_by": "system", "date": "2024-01-01"},
    "trash": {"id": "6129486856212979482", "fallback": "🗑️", "added_by": "system", "date": "2024-01-01"},
    "top4": {"id": "6129409825974525149", "fallback": "🔝", "added_by": "system", "date": "2024-01-01"},
    "skull4": {"id": "6129711392808247546", "fallback": "💀", "added_by": "system", "date": "2024-01-01"},
    "moai2": {"id": "6129410818111970687", "fallback": "🗿", "added_by": "system", "date": "2024-01-01"},
    "red_heart": {"id": "6129562112629938847", "fallback": "❤️", "added_by": "system", "date": "2024-01-01"},
    "lightning": {"id": "6129695952400820630", "fallback": "⚡", "added_by": "system", "date": "2024-01-01"},
    "robot": {"id": "6129873536413605540", "fallback": "🤖", "added_by": "system", "date": "2024-01-01"},
    "blue_circle": {"id": "6129651868856491132", "fallback": "🔵", "added_by": "system", "date": "2024-01-01"},
    "cool": {"id": "6132198982031513203", "fallback": "😎", "added_by": "system", "date": "2024-01-01"},
    "star16": {"id": "6129663516807796597", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "fast_forward": {"id": "6129802875611651951", "fallback": "⏩", "added_by": "system", "date": "2024-01-01"},
    "fire2": {"id": "6129897266107915247", "fallback": "🔥", "added_by": "system", "date": "2024-01-01"},
    "two": {"id": "6129426142555282578", "fallback": "2️⃣", "added_by": "system", "date": "2024-01-01"},
    "one": {"id": "6129873970205302255", "fallback": "1️⃣", "added_by": "system", "date": "2024-01-01"},
    "wine": {"id": "6129527246085429728", "fallback": "🍷", "added_by": "system", "date": "2024-01-01"},
    "wifi": {"id": "6129934104042412999", "fallback": "🛜", "added_by": "system", "date": "2024-01-01"},
    "cool2": {"id": "6131893910504480009", "fallback": "😎", "added_by": "system", "date": "2024-01-01"},
    "party2": {"id": "6129758753412619088", "fallback": "🥳", "added_by": "system", "date": "2024-01-01"},
    "moai3": {"id": "6132118786402163360", "fallback": "🗿", "added_by": "system", "date": "2024-01-01"},
    "fire3": {"id": "6129418815341077483", "fallback": "🔥", "added_by": "system", "date": "2024-01-01"},
    "slight_smile2": {"id": "6129911435205024348", "fallback": "🙂", "added_by": "system", "date": "2024-01-01"},
    "squint": {"id": "6129794302856927889", "fallback": "😝", "added_by": "system", "date": "2024-01-01"},
    "thumbs4": {"id": "6129926467590560665", "fallback": "👍", "added_by": "system", "date": "2024-01-01"},
    "slight_smile3": {"id": "6129786503196319136", "fallback": "🙂", "added_by": "system", "date": "2024-01-01"},
    "open_mouth": {"id": "6129795982189141421", "fallback": "😮", "added_by": "system", "date": "2024-01-01"},
    "lol": {"id": "6136389070521114052", "fallback": "🤣", "added_by": "system", "date": "2024-01-01"},
    "three": {"id": "6136461792907370226", "fallback": "3️⃣", "added_by": "system", "date": "2024-01-01"},
    "grin": {"id": "6138557745537751767", "fallback": "😀", "added_by": "system", "date": "2024-01-01"},
    "grin2": {"id": "6136269971077995421", "fallback": "😀", "added_by": "system", "date": "2024-01-01"},
    "grin3": {"id": "6138763921147829284", "fallback": "😀", "added_by": "system", "date": "2024-01-01"},
    "grin4": {"id": "6136565769770637814", "fallback": "😀", "added_by": "system", "date": "2024-01-01"},
    "grin5": {"id": "6138443507997612595", "fallback": "😀", "added_by": "system", "date": "2024-01-01"},
    "red_heart2": {"id": "6138957710072223834", "fallback": "❤️", "added_by": "system", "date": "2024-01-01"},
    "sparkling_heart": {"id": "6136406830210882173", "fallback": "💖", "added_by": "system", "date": "2024-01-01"},
    "crying_cat": {"id": "6136308217761766184", "fallback": "😿", "added_by": "system", "date": "2024-01-01"},
    "smile4": {"id": "6138514890354071735", "fallback": "😊", "added_by": "system", "date": "2024-01-01"},
    "skull5": {"id": "6138465562654678199", "fallback": "💀", "added_by": "system", "date": "2024-01-01"},
    "fast_forward2": {"id": "6136514547990666308", "fallback": "⏩", "added_by": "system", "date": "2024-01-01"},
    "heart_arrow2": {"id": "6154335299309672955", "fallback": "💘", "added_by": "system", "date": "2024-01-01"},
    "heart3": {"id": "6156715484285770345", "fallback": "❤", "added_by": "system", "date": "2024-01-01"},
    "gift11": {"id": "6156880045957716584", "fallback": "🎁", "added_by": "system", "date": "2024-01-01"},
    "arrow_right": {"id": "6154421933095000846", "fallback": "➡️", "added_by": "system", "date": "2024-01-01"},
    "sad": {"id": "6156827067536120729", "fallback": "😞", "added_by": "system", "date": "2024-01-01"},
    "arrow_right2": {"id": "6156945144777022169", "fallback": "➡️", "added_by": "system", "date": "2024-01-01"},
    "skull6": {"id": "6156936361568901831", "fallback": "💀", "added_by": "system", "date": "2024-01-01"},
    "star17": {"id": "6156541396376361727", "fallback": "🌟", "added_by": "system", "date": "2024-01-01"},
    "hundred": {"id": "6154257607646255757", "fallback": "💯", "added_by": "system", "date": "2024-01-01"},
    "check5": {"id": "6156558816763714393", "fallback": "✅", "added_by": "system", "date": "2024-01-01"},
    "duck": {"id": "6156434919842127016", "fallback": "🦆", "added_by": "system", "date": "2024-01-01"},
    "grin6": {"id": "6154621704908839853", "fallback": "😃", "added_by": "system", "date": "2024-01-01"},
    "trophy": {"id": "6156436440260549720", "fallback": "🏆", "added_by": "system", "date": "2024-01-01"},
    "calendar3": {"id": "6154177180088670691", "fallback": "🗓", "added_by": "system", "date": "2024-01-01"},
    "heart_eyes": {"id": "6156599245290872488", "fallback": "😍", "added_by": "system", "date": "2024-01-01"},
    "pushpin": {"id": "6154294879372450069", "fallback": "📌", "added_by": "system", "date": "2024-01-01"},
    "eye": {"id": "6154239663272893260", "fallback": "👁", "added_by": "system", "date": "2024-01-01"},
}

user_data_store = {}

def save_emojis():
    try:
        with open(EMOJI_FILE, 'w', encoding='utf-8') as f:
            json.dump(PREMIUM_EMOJIS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving emojis: {e}")

def load_emojis():
    global PREMIUM_EMOJIS
    try:
        if os.path.exists(EMOJI_FILE):
            with open(EMOJI_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                for key, value in loaded.items():
                    if key not in PREMIUM_EMOJIS:
                        PREMIUM_EMOJIS[key] = value
                logger.info(f"Loaded {len(loaded)} emojis from file")
    except Exception as e:
        logger.error(f"Error loading emojis: {e}")

def get_emoji_html(name):
    if name in PREMIUM_EMOJIS:
        data = PREMIUM_EMOJIS[name]
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return ""

def format_with_emojis(text):
    return process_text_with_emojis(text)

async def is_admin_in_channel(context, user_id, channel_username):
    try:
        chat = await context.bot.get_chat(chat_id=channel_username)
        chat_member = await context.bot.get_chat_member(chat_id=chat.id, user_id=user_id)
        
        return chat_member.status in ["administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    verified = get_emoji_html("verified")
    stars = get_emoji_html("stars")
    
    message = f"{verified} Premium Emoji Broadcast Bot {stars}\n\n" + format_with_emojis(
        "'top' How to use 'done':\n"
        "1. Use /ads to see all emojis\n"
        "2. Use /ads1, /ads2, /ads3, /ads4 to see emojis in groups\n"
        "3. Use /myemojis to see your added emojis\n"
        "4. Use /broadcast to broadcast with 'emoji_name' (Admin only)\n"
        "5. Use /broadcast2 to broadcast with normal emojis (Auto convert to premium) - Now with Buttons!\n"
        "6. Use /addemoji to add new emoji\n"
        "7. Use /addemojilink to add emoji from link (Auto name & ID)\n"
        "8. Use /addemoji2 to add multiple emojis at once (id name fallback format)\n"
        "9. Use /help for more info\n\n"
        "Example text: welcome to premium emoji bot 'verified'\n"
        "Replace 'verified' with any emoji name from /ads"
    )
    await update.message.reply_text(message, parse_mode="HTML")

async def ads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji_list = []
    for name, data in list(PREMIUM_EMOJIS.items())[:50]:
        emoji_html = get_emoji_html(name)
        fallback = data.get("fallback", "❓")
        added_by = data.get("added_by", "system")
        emoji_list.append(f"{emoji_html} {name} - {fallback} (by {added_by})")
    
    top = get_emoji_html("top")
    stars = get_emoji_html("stars")
    
    message = f"{top} Available Premium Emojis ({len(PREMIUM_EMOJIS)}) {stars}\n\n" + \
              "\n".join(emoji_list) + \
              format_with_emojis(
                  "\n\n'good' Usage: Type emoji names in single quotes like 'emoji_name'\n\n"
                  "Example: Hello 'verified' 'stars' 'dollar'\n\n"
                  "Use /ads1, /ads2, /ads3, /ads4 to see more emojis"
              )
    await update.message.reply_text(message, parse_mode="HTML")

async def ads1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji_list = []
    items = list(PREMIUM_EMOJIS.items())
    for name, data in items[:100]:
        emoji_html = get_emoji_html(name)
        fallback = data.get("fallback", "❓")
        added_by = data.get("added_by", "system")
        emoji_list.append(f"{emoji_html} {name} - {fallback} (by {added_by})")
    
    top = get_emoji_html("top")
    stars = get_emoji_html("stars")
    
    message = f"{top} Premium Emojis (1-100) {stars}\n\n" + \
              "\n".join(emoji_list) + \
              format_with_emojis("\n\nUse /ads2, /ads3, /ads4 to see more")
    await update.message.reply_text(message, parse_mode="HTML")

async def ads2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji_list = []
    items = list(PREMIUM_EMOJIS.items())
    for name, data in items[100:200]:
        emoji_html = get_emoji_html(name)
        fallback = data.get("fallback", "❓")
        added_by = data.get("added_by", "system")
        emoji_list.append(f"{emoji_html} {name} - {fallback} (by {added_by})")
    
    if emoji_list:
        top = get_emoji_html("top")
        stars = get_emoji_html("stars")
        
        message = f"{top} Premium Emojis (101-200) {stars}\n\n" + \
                  "\n".join(emoji_list) + \
                  format_with_emojis("\n\nUse /ads3 and /ads4 to see more")
        await update.message.reply_text(message, parse_mode="HTML")
    else:
        await update.message.reply_text("No emojis in this range.", parse_mode="HTML")

async def ads3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji_list = []
    items = list(PREMIUM_EMOJIS.items())
    for name, data in items[200:300]:
        emoji_html = get_emoji_html(name)
        fallback = data.get("fallback", "❓")
        added_by = data.get("added_by", "system")
        emoji_list.append(f"{emoji_html} {name} - {fallback} (by {added_by})")
    
    if emoji_list:
        top = get_emoji_html("top")
        stars = get_emoji_html("stars")
        
        message = f"{top} Premium Emojis (201-300) {stars}\n\n" + \
                  "\n".join(emoji_list) + \
                  format_with_emojis("\n\nUse /ads4 to see more")
        await update.message.reply_text(message, parse_mode="HTML")
    else:
        await update.message.reply_text("No emojis in this range.", parse_mode="HTML")

async def ads4_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji_list = []
    items = list(PREMIUM_EMOJIS.items())
    for name, data in items[300:]:
        emoji_html = get_emoji_html(name)
        fallback = data.get("fallback", "❓")
        added_by = data.get("added_by", "system")
        emoji_list.append(f"{emoji_html} {name} - {fallback} (by {added_by})")
    
    if emoji_list:
        top = get_emoji_html("top")
        stars = get_emoji_html("stars")
        
        message = f"{top} Premium Emojis (301+) {stars}\n\n" + \
                  "\n".join(emoji_list)
        await update.message.reply_text(message, parse_mode="HTML")
    else:
        await update.message.reply_text("No more emojis to display.", parse_mode="HTML")

async def myemojis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.username or update.effective_user.first_name
    
    user_emojis = []
    for name, data in PREMIUM_EMOJIS.items():
        if data.get("added_by", "").lower() == str(user_id).lower() or data.get("added_by", "") == user_name:
            emoji_html = get_emoji_html(name)
            date = data.get("date", "Unknown")
            user_emojis.append(f"{emoji_html} {name} (added: {date})")
    
    if user_emojis:
        top = get_emoji_html("top")
        stars = get_emoji_html("stars")
        
        message = f"{top} Your Added Emojis ({len(user_emojis)}) {stars}\n\n" + \
                  "\n".join(user_emojis) + \
                  format_with_emojis(
                      "\n\n'good' Use /addemoji to add more emojis"
                  )
    else:
        message = format_with_emojis(
            "❌ You haven't added any emojis yet!\n\n"
            "'good' Use /addemoji to add your first emoji\n"
            "Everyone will be able to use your added emojis!"
        )
    
    await update.message.reply_text(message, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    verified = get_emoji_html("verified")
    stars = get_emoji_html("stars")
    
    message = f"{verified} Help Guide\n\n" + format_with_emojis(
        "'stars' Commands 'top':\n"
        "• /start - Start the bot\n"
        "• /ads - Show ALL available emojis\n"
        "• /ads1 to /ads4 - Show emojis in groups\n"
        "• /myemojis - Show emojis YOU added\n"
        "• /broadcast - Broadcast with 'emoji_name' (Admin only)\n"
        "• /broadcast2 - Broadcast with normal emojis (Auto convert to premium) - Now with Buttons!\n"
        "• /addemoji - Add new custom emoji\n"
        "• /addemojilink - Add emoji from link (Auto name & ID)\n"
        "• /addemoji2 - Add multiple emojis at once (id name fallback format)\n"
        "• /help - Show this help\n\n"
        "'lock' Admin Requirement 'verified':\n"
        "• Must be admin in target channel\n"
        "• Bot must be admin in channel\n"
        "• Only admins can broadcast\n\n"
        "'good' Emoji Sharing 'heart':\n"
        "• Anyone can add emojis\n"
        "• Everyone can use added emojis\n"
        "• Check /myemojis for your contributions"
    )
    await update.message.reply_text(message, parse_mode="HTML")

async def addemoji_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id] = {"step": "waiting_emoji_name", "user_name": update.effective_user.username or update.effective_user.first_name}
    
    plus = get_emoji_html("done")
    await update.message.reply_text(
        f"{plus} Adding New Emoji\n\n" + format_with_emojis(
            "Step 1️⃣: Send the emoji name (no spaces, use underscore)\n"
            "Example: fire_emoji or cool_badge\n\n"
            "'stars' Everyone will see and use your emoji!"
        ),
        parse_mode="HTML"
    )

async def addemojilink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id] = {"step": "waiting_emoji_link", "user_name": update.effective_user.username or update.effective_user.first_name}
    
    plus = get_emoji_html("done")
    await update.message.reply_text(
        f"{plus} Adding Emoji from Link\n\n" + format_with_emojis(
            "Send the emoji link or forward a message containing the emoji\n"
            "Example: https://t.me/addemoji/KripanshEmojis_by_fStikBot\n\n"
            "✨ The bot will automatically extract:\n"
            "• Emoji ID\n"
            "• Fallback emoji\n"
            "• Auto-generate name\n"
            "✨ Everyone can use this emoji after adding!"
        ),
        parse_mode="HTML"
    )

async def addemoji2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.username or update.effective_user.first_name
    
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ Please provide emoji details!\n\n"
            "Format: `/addemoji2 id1 name1 fallback1 id2 name2 fallback2 ...`\n\n"
            "Example: `/addemoji2 123456789 heart ❤️ 987654321 star ⭐`\n\n"
            "You can add unlimited emojis in one command!\n"
            "Names should not contain spaces (use underscore)",
            parse_mode="HTML"
        )
        return
    
    if len(args) % 3 != 0:
        await update.message.reply_text(
            f"❌ Invalid format! You provided {len(args)} arguments, which is not a multiple of 3.\n\n"
            "Each emoji needs: ID, Name, Fallback\n"
            "Example: `/addemoji2 123 heart ❤️ 456 star ⭐ 789 fire 🔥`",
            parse_mode="HTML"
        )
        return
    
    added_emojis = []
    failed_emojis = []
    duplicates = []
    
    total_emojis = len(args) // 3
    
    for i in range(0, len(args), 3):
        emoji_id = args[i]
        emoji_name = args[i+1].lower()
        fallback_text = args[i+2]
        
        if ' ' in emoji_name:
            failed_emojis.append(f"{emoji_name} (name contains spaces)")
            continue
        
        if emoji_name in PREMIUM_EMOJIS:
            duplicates.append(emoji_name)
            continue
        
        PREMIUM_EMOJIS[emoji_name] = {
            "id": emoji_id,
            "fallback": fallback_text,
            "added_by": user_name,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        added_emojis.append(emoji_name)
    
    if added_emojis:
        save_emojis()
    
    response_parts = []
    
    if added_emojis:
        plus_emoji = get_emoji_html("done")
        response_parts.append(f"{plus_emoji} Successfully added {len(added_emojis)}/{total_emojis} emoji(s):\n")
        for name in added_emojis[:10]:
            emoji_html = get_emoji_html(name)
            response_parts.append(f"  {emoji_html} {name}")
        if len(added_emojis) > 10:
            response_parts.append(f"  ... and {len(added_emojis) - 10} more")
    
    if duplicates:
        warning_emoji = get_emoji_html("warning")
        response_parts.append(f"\n{warning_emoji} Duplicate names (skipped): {len(duplicates)}")
        response_parts.append(f"  {', '.join(duplicates[:5])}")
        if len(duplicates) > 5:
            response_parts.append(f"  ... and {len(duplicates) - 5} more")
    
    if failed_emojis:
        cry_emoji = get_emoji_html("crying")
        response_parts.append(f"\n{cry_emoji} Failed to add: {len(failed_emojis)}")
        for fail in failed_emojis[:5]:
            response_parts.append(f"  • {fail}")
        if len(failed_emojis) > 5:
            response_parts.append(f"  ... and {len(failed_emojis) - 5} more")
    
    if not added_emojis:
        response_parts.insert(0, "❌ No emojis were added.")
    
    response_parts.append("\n✨ Everyone can now use these emojis!\nCheck /ads to see all emojis")
    
    await update.message.reply_text("\n".join(response_parts), parse_mode="HTML")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    broadcast_emoji = get_emoji_html("telegram")
    await update.message.reply_text(
        f"{broadcast_emoji} Broadcast Setup (Admin Only)\n\n" + format_with_emojis(
            "⚠️ You must be admin in target channel\n"
            "Step 1️⃣: Send the text you want to broadcast\n"
            "Include emoji names in single quotes like 'emoji_name'\n\n"
            "'top' Example 'done':\n"
            "Welcome to our premium channel 'verified' Get offers 'dollar' 'stars'"
        ),
        parse_mode="HTML"
    )
    
    user_data_store[user_id] = {"step": "waiting_text"}

async def broadcast2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    broadcast_emoji = get_emoji_html("heart")
    await update.message.reply_text(
        f"{broadcast_emoji} Broadcast 2.0 (Auto Convert Emojis + Buttons!)\n\n" + format_with_emojis(
            "⚠️ You must be admin in target channel\n"
            "📝 Step 1️⃣: Send your message with normal emojis\n"
            "✨ You can send:\n"
            "• Text messages\n"
            "• Photos with captions\n\n"
            "Example: Hello 🙂 Welcome to our premium channel ❤️ Get offers 💎\n\n"
            "✨ Normal emojis will automatically convert to premium emojis!\n"
            "✨ Buttons will also get matching premium emoji icons!\n"
            "✨ After message, you can add buttons with custom colors!"
        ),
        parse_mode="HTML"
    )
    
    user_data_store[user_id] = {
        "step": "waiting_media2",
        "buttons": []
    }

def get_emoji_id_from_text(text):
    """Extract best matching emoji ID from text (1st mapping, 2nd similar, 3rd fallback)"""
    if not text:
        return PREMIUM_EMOJIS.get("verified", {}).get("id")
    
    # Extract all emojis from text
    emoji_pattern = re.compile(
        r'('
        r'[\U0001F1E6-\U0001F1FF]{2}|'
        r'[\U0001F600-\U0001F64F]|'
        r'[\U0001F300-\U0001F5FF]|'
        r'[\U0001F680-\U0001F6FF]|'
        r'[\U0001F700-\U0001F77F]|'
        r'[\U0001F780-\U0001F7FF]|'
        r'[\U0001F800-\U0001F8FF]|'
        r'[\U0001F900-\U0001F9FF]|'
        r'[\U0001FA70-\U0001FAFF]|'
        r'[\u2600-\u26FF]|'
        r'[\u2700-\u27BF]|'
        r'[\u2300-\u23FF]|'
        r'[\uFE0F]|'
        r'[\u200D]'
        r')+',
        flags=re.UNICODE
    )
    
    emojis_found = emoji_pattern.findall(text)
    
    if emojis_found:
        # Try 1st mapping: exact match
        for emoji in emojis_found:
            for name, data in PREMIUM_EMOJIS.items():
                if data["fallback"] == emoji:
                    return data["id"]
        
        # Try 2nd mapping: similar emoji
        for emoji in emojis_found:
            similar = get_similar_emoji(emoji)
            if similar:
                return similar["id"]
    
    # 3rd mapping: return first system emoji (verified)
    return PREMIUM_EMOJIS.get("verified", {}).get("id")

def get_random_fallback_emoji():
    random_name = random.choice(FALLBACK_EMOJIS_LIST)
    if random_name in PREMIUM_EMOJIS:
        return PREMIUM_EMOJIS[random_name]
    return PREMIUM_EMOJIS.get("stars", {"id": "6235403472741603087", "fallback": "⭐"})

def get_similar_emoji(emoji):
    similar_map = {
        "😊": "smile", "😃": "teeth", "😄": "teeth", "😁": "teeth",
        "😂": "cry", "🤣": "cry", "😍": "heart", "🥰": "heart",
        "😘": "heart", "😗": "heart", "😙": "heart", "😚": "heart",
        "🙂": "smiling", "🙃": "smiling", "😉": "seeing_up", "😇": "angel",
        "🥲": "smiling", "😔": "crying", "😌": "smiling", "😞": "crying",
        "😟": "crying", "😢": "crying", "😭": "crying", "😤": "frozen",
        "😠": "frozen", "😡": "frozen", "🤬": "frozen", "😎": "flex",
        "🤓": "nerd", "🧐": "nerd", "🥸": "seeing_up", "😏": "smiling",
        "😒": "smiling", "😓": "crying", "😪": "crying", "😴": "crying",
        "😵": "crying", "😲": "crying", "😮": "crying", "🤯": "crying",
        "😨": "crying", "😰": "crying", "😱": "crying", "😖": "crying",
        "😣": "crying", "😫": "crying", "😩": "crying", "🥺": "crying",
        "🥹": "crying", "😳": "crying", "🤔": "thinking", "🤨": "nerd",
        "😐": "smiling", "😑": "smiling", "😶": "smiling",
        "🤐": "lock", "😯": "crying", "😦": "crying", "😧": "crying",
        "❤️": "heart", "🧡": "heart", "💛": "heart", "💚": "heart",
        "💙": "blue_verification", "💜": "heart", "🖤": "skills",
        "🤍": "white_heart", "🤎": "don", "💔": "heart",
        "❤️‍🔥": "heartfire", "💕": "heart", "💞": "heart",
        "💓": "heart", "💗": "heart", "💖": "heart",
        "💘": "heart", "💝": "heart", "💟": "heart", "👍": "done",
        "👎": "block", "👊": "good", "✊": "good", "🤛": "good",
        "🤜": "good", "👏": "good", "🙌": "good", "🤝": "bro",
        "👌": "yes", "🤞": "yes", "✌️": "yes", "🤟": "yes",
        "🤘": "yes", "👈": "point_up", "👉": "point_up", "👆": "point_up",
        "👇": "point_up", "☝️": "point_up", "⭐": "stars", "🌟": "stars",
        "✨": "sparkle", "💫": "motion", "🔥": "fire", "💥": "fire",
        "⚡": "fire", "💨": "frozen", "💦": "crying", "💎": "blue_verification",
        "🔮": "blue_verification", "🎁": "gift", "🎀": "gift", "🎈": "gift",
        "🎉": "gift", "🎊": "gift", "🎭": "disguise", "👑": "crown",
        "💍": "crown", "💄": "crown", "👗": "crown", "👠": "crown",
        "👡": "crown", "👢": "crown", "👔": "crown", "👕": "crown",
        "👖": "crown", "🧣": "crown", "🧤": "crown", "🧥": "crown",
        "🧦": "crown", "👓": "nerd", "🕶️": "flex", "🥽": "nerd",
        "🥼": "nerd", "🦺": "nerd", "🎩": "crown", "🧢": "crown",
        "⛑️": "crown", "👒": "crown", "💼": "crown", "🎒": "crown",
        "👝": "crown", "👛": "crown", "👜": "crown", "📿": "bookmark",
        "🔹": "diamond", "🔸": "diamond", "🔷": "blue_verification", "🔶": "diamond",
        "💡": "light", "🔦": "light", "📱": "github", "💻": "github",
        "🖥️": "github", "🖨️": "github", "⌨️": "github", "🖱️": "github",
        "🖲️": "github", "📷": "camera", "📸": "camera", "📹": "camera",
        "🎥": "camera", "📽️": "camera", "🎬": "fast_forward", "📺": "fast_forward",
        "📻": "telegram", "🎙️": "telegram", "🎚️": "slider", "🎛️": "slider",
        "⏯️": "fast_forward", "⏩": "fast_forward", "⏪": "fast_forward",
        "🔔": "bell", "🔕": "bell", "📢": "megaphone", "📣": "megaphone",
        "💬": "bubble", "💭": "thought", "🗯️": "bubble", "📌": "pin",
        "📍": "pin", "🔖": "bookmark", "🔗": "link", "📎": "link",
        "🖇️": "link", "📏": "chart", "📐": "chart", "📊": "chart",
        "📈": "chart", "📉": "chart", "🗓️": "calendar", "📅": "calendar",
        "📆": "calendar", "⏰": "alarm", "⏲️": "alarm", "⌚": "alarm",
        "🕰️": "alarm", "🌍": "earth", "🌎": "earth", "🌏": "earth",
        "🇮🇳": "india", "🏁": "flag", "🚩": "flag", "🎌": "flag",
        "🏴": "flag", "🏳️": "flag", "💰": "dollar", "💵": "dollar",
        "💶": "dollar", "💷": "dollar", "💴": "dollar", "💸": "dollar",
        "💳": "card", "💯": "hundred", "🔝": "top", "✅": "verified",
        "✔️": "tick", "☑️": "check", "❌": "block", "❎": "block",
        "🚫": "block", "🚸": "warning", "⚠️": "warning", "❗": "exclaim",
        "❕": "exclaim", "‼️": "exclaim", "⁉️": "exclaim", "🍼": "bottle",
        "🍏": "apple", "🍷": "wine", "🍾": "champagne", "🥃": "sigma",
        "🍂": "don", "🎄": "xmas", "🎃": "ghost", "👻": "ghost",
        "👽": "robot", "🤖": "robot", "👾": "robot", "🎮": "robot",
        "🕹️": "robot", "🔒": "lock", "🔓": "lock", "🔐": "lock",
        "🔑": "lock", "🚗": "car", "🚘": "car", "🚙": "car", "🚕": "car",
        "🚖": "car", "🚌": "car", "🚎": "car", "🏎️": "car", "🚓": "car",
        "🚑": "car", "🚒": "car", "🚐": "car", "🚚": "car", "🚛": "car",
        "🚜": "car", "🛵": "car", "🏍️": "car", "🚲": "car", "🚀": "rocket",
        "🛸": "rocket", "🛰️": "rocket", "💺": "chair", "🛋️": "chair",
        "🛏️": "chair", "🛌": "chair", "🧸": "teddy", "🎠": "party",
        "🎡": "party", "🎢": "party", "🎪": "party", "🎯": "target",
        "🎳": "target", "🎮": "game", "🎲": "game", "🧩": "game"
    }
    
    if emoji in similar_map and similar_map[emoji] in PREMIUM_EMOJIS:
        return PREMIUM_EMOJIS[similar_map[emoji]]
    
    return None

def convert_normal_emojis_to_premium(text):
    if not text:
        return text
    
    emoji_pattern = re.compile(
        r'('
        r'[\U0001F1E6-\U0001F1FF]{2}|'
        r'[\U0001F600-\U0001F64F]|'
        r'[\U0001F300-\U0001F5FF]|'
        r'[\U0001F680-\U0001F6FF]|'
        r'[\U0001F700-\U0001F77F]|'
        r'[\U0001F780-\U0001F7FF]|'
        r'[\U0001F800-\U0001F8FF]|'
        r'[\U0001F900-\U0001F9FF]|'
        r'[\U0001FA70-\U0001FAFF]|'
        r'[\u2600-\u26FF]|'
        r'[\u2700-\u27BF]|'
        r'[\u2300-\u23FF]|'
        r'[\uFE0F]|'
        r'[\u200D]'
        r')+',
        flags=re.UNICODE
    )
    
    def replace_emoji(match):
        emoji = match.group(0)
        
        for name, data in PREMIUM_EMOJIS.items():
            if data["fallback"] == emoji:
                return f'<tg-emoji emoji-id="{data["id"]}">{emoji}</tg-emoji>'
        
        similar = get_similar_emoji(emoji)
        if similar:
            return f'<tg-emoji emoji-id="{similar["id"]}">{emoji}</tg-emoji>'
        
        random_emoji = get_random_fallback_emoji()
        return f'<tg-emoji emoji-id="{random_emoji["id"]}">{random_emoji["fallback"]}</tg-emoji>'
    
    result = emoji_pattern.sub(replace_emoji, text)
    return result

async def button_prompt_kb():
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Add Buttons", callback_data="btn_yes"),
            InlineKeyboardButton("❌ No, Skip Buttons", callback_data="btn_no")
        ]
    ])
    return keyboard

async def button_type_kb():
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 URL Button", callback_data="btn_type_url"),
            InlineKeyboardButton("📋 Text Button (Copy)", callback_data="btn_type_text")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="btn_cancel")]
    ])
    return keyboard

async def button_colors_kb():
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔵 Blue", callback_data="btn_color_primary"),
            InlineKeyboardButton("🟢 Green", callback_data="btn_color_success"),
            InlineKeyboardButton("🔴 Red", callback_data="btn_color_danger")
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="btn_back_to_type")]
    ])
    return keyboard

async def confirm_cancel_kb():
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ CONFIRM", callback_data="btn_confirm"),
            InlineKeyboardButton("❌ CANCEL", callback_data="btn_cancel_broadcast")
        ]
    ])
    return keyboard

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if user_id not in user_data_store:
        await query.edit_message_text("Session expired. Please use /broadcast2 again.")
        return
    
    if data == "btn_yes":
        user_data_store[user_id]["step"] = "waiting_button_type"
        await query.edit_message_text(
            "🎯 Select button type:",
            reply_markup=await button_type_kb()
        )
    
    elif data == "btn_no":
        user_data_store[user_id]["step"] = "waiting_channel2"
        user_data_store[user_id]["skip_buttons"] = True
        await query.edit_message_text(
            "✅ No buttons added. Now send the channel username (with @)\n\n"
            "Example: @yourchannel\n\n"
            "⚠️ You must be admin in that channel"
        )
    
    elif data == "btn_type_url":
        user_data_store[user_id]["temp_button"] = {"type": "url"}
        user_data_store[user_id]["step"] = "waiting_button_text"
        await query.edit_message_text(
            "🔗 Enter button text (max 30 characters):\n\n"
            "Example: Visit Website"
        )
    
    elif data == "btn_type_text":
        user_data_store[user_id]["temp_button"] = {"type": "text"}
        user_data_store[user_id]["step"] = "waiting_button_text"
        await query.edit_message_text(
            "📋 Enter button text (max 30 characters):\n\n"
            "Example: Copy Code"
        )
    
    elif data == "btn_cancel":
        user_data_store[user_id]["step"] = "waiting_channel2"
        user_data_store[user_id]["skip_buttons"] = True
        await query.edit_message_text(
            "❌ Button cancelled. Now send the channel username (with @)"
        )
    
    elif data == "btn_back_to_type":
        user_data_store[user_id]["step"] = "waiting_button_type"
        await query.edit_message_text(
            "🎯 Select button type:",
            reply_markup=await button_type_kb()
        )
    
    elif data.startswith("btn_color_"):
        color = data.replace("btn_color_", "")
        user_data_store[user_id]["temp_button"]["color"] = color
        button = user_data_store[user_id].pop("temp_button")
        user_data_store[user_id]["buttons"].append(button)
        
        await query.edit_message_text(
            f"✅ Button added!\n\n"
            f"Type: {'🔗 URL' if button['type'] == 'url' else '📋 Text'}\n"
            f"Text: {button['text']}\n"
            f"Color: {color.upper()}\n\n"
            f"Do you want to add another button?\n"
            f"Send /addbutton to add more\n"
            f"Or send /donebuttons when finished"
        )
        user_data_store[user_id]["step"] = "waiting_more_buttons"
    
    elif data == "btn_confirm":
        user_data_store[user_id]["step"] = "waiting_channel2"
        await query.edit_message_text(
            "✅ Broadcast confirmed! Now send the channel username (with @)\n\n"
            "Example: @yourchannel\n\n"
            "⚠️ You must be admin in that channel"
        )
    
    elif data == "btn_cancel_broadcast":
        del user_data_store[user_id]
        await query.edit_message_text("❌ Broadcast cancelled!")

def process_text_with_emojis(text):
    def replace_emoji(match):
        emoji_name = match.group(1).strip().lower()
        
        if emoji_name in PREMIUM_EMOJIS:
            data = PREMIUM_EMOJIS[emoji_name]
            emoji_id = data.get("id")
            fallback = data.get("fallback", "❓")
            return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
        
        return match.group(0)
    
    pattern = r"'([^']+)'"
    result = re.sub(pattern, replace_emoji, text)
    
    return result

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None:
        return
    
    user_id = update.effective_user.id
    
    if user_id not in user_data_store:
        return
    
    step = user_data_store[user_id].get("step")
    
    if step == "waiting_emoji_name":
        emoji_name = update.message.text.strip().lower()
        
        if ' ' in emoji_name:
            error_emoji = get_emoji_html("crying")
            await update.message.reply_text(
                f"{error_emoji} Emoji name cannot contain spaces. Use underscore (_) instead.\n"
                "Example: fire_emoji\n\n"
                "Send emoji name again:",
                parse_mode="HTML"
            )
            return
        
        if emoji_name in PREMIUM_EMOJIS:
            existing_emoji = get_emoji_html(emoji_name)
            await update.message.reply_text(
                f"❌ Emoji name '{emoji_name}' already exists! {existing_emoji}\n"
                f"Choose a different name:",
                parse_mode="HTML"
            )
            return
        
        user_data_store[user_id]["emoji_name"] = emoji_name
        user_data_store[user_id]["step"] = "waiting_emoji_data"
        
        done_emoji = get_emoji_html("done")
        await update.message.reply_text(
            f"{done_emoji} Emoji name: {emoji_name}\n\n"
            "Step 2️⃣: Now forward a message with emoji or send the emoji ID\n\n"
            "⭐ Everyone will be able to use this emoji!",
            parse_mode="HTML"
        )
    
    elif step == "waiting_emoji_data":
        emoji_name = user_data_store[user_id]["emoji_name"]
        message_text = update.message.text or ""
        
        emoji_id = None
        fallback_text = None
        
        if update.message.entities:
            for entity in update.message.entities:
                if entity.type == "custom_emoji":
                    emoji_id = str(entity.custom_emoji_id)
                    if update.message.text:
                        fallback_text = update.message.text[entity.offset:entity.offset + entity.length]
                    break
        
        if not emoji_id and message_text.isdigit():
            emoji_id = message_text
            fallback_text = "❓"
        
        if not emoji_id:
            match = re.search(r'(\d{15,20})', message_text)
            if match:
                emoji_id = match.group(1)
                fallback_text = "❓"
        
        if not emoji_id and update.message.forward_from:
            if update.message.caption_entities:
                for entity in update.message.caption_entities:
                    if entity.type == "custom_emoji":
                        emoji_id = str(entity.custom_emoji_id)
                        if update.message.caption:
                            fallback_text = update.message.caption[entity.offset:entity.offset + entity.length]
                        break
        
        if emoji_id:
            if not fallback_text or fallback_text == "❓":
                await update.message.reply_text(
                    f"✅ Emoji ID: {emoji_id}\n\n"
                    "Please send the fallback emoji character:\n"
                    "Example: 🔥 or ⭐"
                )
                user_data_store[user_id]["emoji_id"] = emoji_id
                user_data_store[user_id]["step"] = "waiting_fallback"
                return
            
            user_name = user_data_store[user_id].get("user_name", str(user_id))
            
            PREMIUM_EMOJIS[emoji_name] = {
                "id": emoji_id,
                "fallback": fallback_text,
                "added_by": user_name,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            save_emojis()
            
            del user_data_store[user_id]
            
            new_emoji = f'<tg-emoji emoji-id="{emoji_id}">{fallback_text}</tg-emoji>'
            await update.message.reply_text(
                f"{new_emoji} Emoji added successfully!\n\n" +
                format_with_emojis(
                    f"✅ Added to global emoji list!\n"
                    f"Name: {emoji_name}\n"
                    f"Added by: {user_name}\n"
                    f"Use in text like: example text '{emoji_name}'\n\n"
                    f"'stars' Everyone can now use '{emoji_name}' emoji!\n"
                    f"Check /ads to see all emojis\n"
                    f"Check /myemojis to see your emojis"
                ),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                "❌ Could not extract emoji ID!\n"
                "Please forward a message containing the emoji or send a link to the message.\n\n"
                "Example: https://t.me/addemoji/KripanshEmojis_by_fStikBot\n\n"
                "Or forward a message that contains the custom emoji."
            )
    
    elif step == "waiting_emoji_link":
        message_text = update.message.text or ""
        user_name = user_data_store[user_id].get("user_name", str(user_id))
        
        emoji_id = None
        fallback_text = None
        
        if update.message.entities:
            for entity in update.message.entities:
                if entity.type == "custom_emoji":
                    emoji_id = str(entity.custom_emoji_id)
                    if update.message.text:
                        fallback_text = update.message.text[entity.offset:entity.offset + entity.length]
                    break
        
        if not emoji_id and update.message.forward_from:
            if update.message.caption_entities:
                for entity in update.message.caption_entities:
                    if entity.type == "custom_emoji":
                        emoji_id = str(entity.custom_emoji_id)
                        if update.message.caption:
                            fallback_text = update.message.caption[entity.offset:entity.offset + entity.length]
                        break
        
        if not emoji_id:
            match = re.search(r'(\d{15,20})', message_text)
            if match:
                emoji_id = match.group(1)
        
        if emoji_id:
            if not fallback_text or fallback_text == "❓":
                await update.message.reply_text(
                    f"✅ Emoji ID: {emoji_id}\n\n"
                    "Please send the fallback emoji character:\n"
                    "Example: 🔥 or ⭐"
                )
                user_data_store[user_id]["emoji_id"] = emoji_id
                user_data_store[user_id]["step"] = "waiting_fallback_link"
                return
            
            emoji_name = f"emoji_{fallback_text}"
            if fallback_text in ["❤️", "❤️‍🔥", "💕", "💖", "💗", "💘", "💝"]:
                emoji_name = "heart_auto"
            elif fallback_text in ["😊", "🙂", "😀", "😃", "😄", "😁", "😆", "😂"]:
                emoji_name = "smile_auto"
            elif fallback_text in ["🔥", "⚡", "💥", "💫", "✨", "⭐", "🌟"]:
                emoji_name = "fire_auto"
            elif fallback_text in ["👍", "👎", "👌", "🤝", "👏", "🙌"]:
                emoji_name = "thumbs_auto"
            elif fallback_text in ["⭐", "🌟", "✨", "💫"]:
                emoji_name = "star_auto"
            elif fallback_text in ["💎", "🔮", "💠", "🔹", "🔸"]:
                emoji_name = "gem_auto"
            elif fallback_text in ["🎁", "🎀", "🎈", "🎉", "🎊"]:
                emoji_name = "gift_auto"
            elif fallback_text in ["👑", "💍", "👒"]:
                emoji_name = "crown_auto"
            
            base_name = emoji_name
            counter = 1
            while emoji_name in PREMIUM_EMOJIS:
                emoji_name = f"{base_name}_{counter}"
                counter += 1
            
            PREMIUM_EMOJIS[emoji_name] = {
                "id": emoji_id,
                "fallback": fallback_text,
                "added_by": user_name,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            save_emojis()
            
            del user_data_store[user_id]
            
            new_emoji = f'<tg-emoji emoji-id="{emoji_id}">{fallback_text}</tg-emoji>'
            await update.message.reply_text(
                f"{new_emoji} Emoji added successfully!\n\n" +
                format_with_emojis(
                    f"✅ Auto-added to global emoji list!\n"
                    f"Name: {emoji_name}\n"
                    f"Fallback: {fallback_text}\n"
                    f"Added by: {user_name}\n"
                    f"Use in text like: example text '{emoji_name}'\n\n"
                    f"'stars' Everyone can now use this emoji!\n"
                    f"Check /ads to see all emojis"
                ),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                "❌ Could not extract emoji ID!\n"
                "Please forward a message containing the emoji or send a link to the message.\n\n"
                "Example: https://t.me/addemoji/KripanshEmojis_by_fStikBot\n\n"
                "Or forward a message that contains the custom emoji."
            )
    
    elif step == "waiting_fallback":
        fallback_text = update.message.text.strip()
        emoji_name = user_data_store[user_id]["emoji_name"]
        emoji_id = user_data_store[user_id]["emoji_id"]
        user_name = user_data_store[user_id].get("user_name", str(user_id))
        
        PREMIUM_EMOJIS[emoji_name] = {
            "id": emoji_id,
            "fallback": fallback_text,
            "added_by": user_name,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        save_emojis()
        
        del user_data_store[user_id]
        
        new_emoji = f'<tg-emoji emoji-id="{emoji_id}">{fallback_text}</tg-emoji>'
        await update.message.reply_text(
            f"{new_emoji} Emoji added successfully!\n\n" +
            format_with_emojis(
                f"✅ Added to global emoji list!\n"
                f"Name: {emoji_name}\n"
                f"Added by: {user_name}\n"
                f"Use in text like: example text '{emoji_name}'\n\n"
                f"'stars' Everyone can now use '{emoji_name}' emoji!\n"
                f"Check /ads to see all emojis\n"
                f"Check /myemojis to see your emojis"
            ),
            parse_mode="HTML"
        )
    
    elif step == "waiting_fallback_link":
        fallback_text = update.message.text.strip()
        emoji_id = user_data_store[user_id]["emoji_id"]
        user_name = user_data_store[user_id].get("user_name", str(user_id))
        
        emoji_name = f"emoji_{fallback_text}"
        if fallback_text in ["❤️", "❤️‍🔥", "💕", "💖", "💗", "💘", "💝"]:
            emoji_name = "heart_auto"
        elif fallback_text in ["😊", "🙂", "😀", "😃", "😄", "😁", "😆", "😂"]:
            emoji_name = "smile_auto"
        elif fallback_text in ["🔥", "⚡", "💥", "💫", "✨", "⭐", "🌟"]:
            emoji_name = "fire_auto"
        elif fallback_text in ["👍", "👎", "👌", "🤝", "👏", "🙌"]:
            emoji_name = "thumbs_auto"
        elif fallback_text in ["⭐", "🌟", "✨", "💫"]:
            emoji_name = "star_auto"
        elif fallback_text in ["💎", "🔮", "💠", "🔹", "🔸"]:
            emoji_name = "gem_auto"
        elif fallback_text in ["🎁", "🎀", "🎈", "🎉", "🎊"]:
            emoji_name = "gift_auto"
        elif fallback_text in ["👑", "💍", "👒"]:
            emoji_name = "crown_auto"
        
        base_name = emoji_name
        counter = 1
        while emoji_name in PREMIUM_EMOJIS:
            emoji_name = f"{base_name}_{counter}"
            counter += 1
        
        PREMIUM_EMOJIS[emoji_name] = {
            "id": emoji_id,
            "fallback": fallback_text,
            "added_by": user_name,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        save_emojis()
        
        del user_data_store[user_id]
        
        new_emoji = f'<tg-emoji emoji-id="{emoji_id}">{fallback_text}</tg-emoji>'
        await update.message.reply_text(
            f"{new_emoji} Emoji added successfully!\n\n" +
            format_with_emojis(
                f"✅ Auto-added to global emoji list!\n"
                f"Name: {emoji_name}\n"
                f"Fallback: {fallback_text}\n"
                f"Added by: {user_name}\n"
                f"Use in text like: example text '{emoji_name}'\n\n"
                f"'stars' Everyone can now use this emoji!\n"
                f"Check /ads to see all emojis"
            ),
            parse_mode="HTML"
        )
    
    elif step == "waiting_text":
        text = update.message.text
        user_data_store[user_id]["text"] = text
        user_data_store[user_id]["is_photo"] = False
        user_data_store[user_id]["step"] = "waiting_buttons"
        
        preview_text = process_text_with_emojis(text)
        
        try:
            preview_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=preview_text,
                parse_mode="HTML"
            )
            
            user_data_store[user_id]["preview_msg_id"] = preview_msg.message_id
            
            await update.message.reply_text(
                "📝 Preview with premium emojis ↑\n\n"
                "Do you want to add buttons to this message?",
                reply_markup=await button_prompt_kb()
            )
            
        except Exception as e:
            error_emoji = get_emoji_html("crying")
            await update.message.reply_text(
                f"{error_emoji} Error: {str(e)}\n\n"
                "Make sure emoji names are correct. Use /ads to check emoji names."
            )
            del user_data_store[user_id]
    
    elif step == "waiting_media2":
        user_data_store[user_id]["step"] = "waiting_buttons"
        
        # Store the original text for button emoji mapping
        if update.message.photo:
            user_data_store[user_id]["is_photo"] = True
            photo = update.message.photo[-1]
            user_data_store[user_id]["photo_file_id"] = photo.file_id
            user_data_store[user_id]["caption"] = update.message.caption or ""
            user_data_store[user_id]["original_text"] = user_data_store[user_id]["caption"]
            converted_caption = convert_normal_emojis_to_premium(user_data_store[user_id]["caption"])
            
            preview_msg = await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo.file_id,
                caption=converted_caption,
                parse_mode="HTML"
            )
            user_data_store[user_id]["preview_msg_id"] = preview_msg.message_id
        else:
            user_data_store[user_id]["is_photo"] = False
            user_data_store[user_id]["text"] = update.message.text
            user_data_store[user_id]["original_text"] = update.message.text
            user_data_store[user_id]["caption"] = ""
            preview_text = convert_normal_emojis_to_premium(update.message.text)
            
            preview_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=preview_text,
                parse_mode="HTML"
            )
            user_data_store[user_id]["preview_msg_id"] = preview_msg.message_id
        
        await update.message.reply_text(
            "📝 Preview with converted premium emojis ↑\n\n"
            "Do you want to add buttons to this message?",
            reply_markup=await button_prompt_kb()
        )
    
    elif step == "waiting_button_text":
        button_text = update.message.text.strip()
        if len(button_text) > 30:
            await update.message.reply_text("❌ Button text too long! Max 30 characters. Try again:")
            return
        
        user_data_store[user_id]["temp_button"] = user_data_store[user_id].get("temp_button", {})
        user_data_store[user_id]["temp_button"]["text"] = button_text
        user_data_store[user_id]["step"] = "waiting_button_data"
        
        if user_data_store[user_id]["temp_button"].get("type") == "url":
            await update.message.reply_text("🔗 Enter the URL (must start with http:// or https://):")
        else:
            await update.message.reply_text("📋 Enter the text to copy when button is clicked:")
    
    elif step == "waiting_button_data":
        button_data = update.message.text.strip()
        
        if user_data_store[user_id]["temp_button"].get("type") == "url":
            if not (button_data.startswith("http://") or button_data.startswith("https://")):
                await update.message.reply_text("❌ Invalid URL! Must start with http:// or https://\n\nTry again:")
                return
            user_data_store[user_id]["temp_button"]["url"] = button_data
        else:
            if len(button_data) > 200:
                await update.message.reply_text("❌ Text too long! Max 200 characters. Try again:")
                return
            user_data_store[user_id]["temp_button"]["copy_text"] = button_data
        
        user_data_store[user_id]["step"] = "waiting_button_color"
        
        await update.message.reply_text(
            "🎨 Select button color:",
            reply_markup=await button_colors_kb()
        )
    
    elif step == "waiting_more_buttons":
        text = update.message.text.strip().lower()
        if text == "/addbutton":
            user_data_store[user_id]["step"] = "waiting_button_type"
            await update.message.reply_text(
                "🎯 Select button type for another button:",
                reply_markup=await button_type_kb()
            )
        elif text == "/donebuttons":
            user_data_store[user_id]["step"] = "waiting_channel2"
            
            buttons = user_data_store[user_id].get("buttons", [])
            
            # Get emoji ID from original text for button icons
            original_text = user_data_store[user_id].get("original_text", "")
            button_icon_id = get_emoji_id_from_text(original_text)
            
            if buttons:
                keyboard = []
                for btn in buttons:
                    btn_color = btn.get("color", "primary")
                    
                    # ✅ CLEAN BUTTON TEXT IF PREMIUM ICON WILL BE ADDED
                    button_text = btn["text"]
                    if button_icon_id:
                        button_text = strip_emojis(button_text)
                    
                    # Create button dict with style
                    button_dict = {
                        "text": button_text
                    }
                    
                    if btn.get("type") == "url":
                        button_dict["url"] = btn["url"]
                    else:
                        button_dict["callback_data"] = f"copy_{btn.get('copy_text', '')[:50]}"
                    
                    # Add style
                    button_dict["style"] = btn_color
                    
                    # Add premium emoji icon
                    if button_icon_id:
                        button_dict["icon_custom_emoji_id"] = button_icon_id
                    
                    keyboard.append([InlineKeyboardButton(**button_dict)])
                
                try:
                    if user_data_store[user_id].get("is_photo"):
                        caption = convert_normal_emojis_to_premium(user_data_store[user_id].get("caption", ""))
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=user_data_store[user_id]["photo_file_id"],
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                    else:
                        text_content = convert_normal_emojis_to_premium(user_data_store[user_id].get("text", ""))
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=text_content,
                            parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                    
                    # Get emoji name for display
                    icon_emoji_name = "unknown"
                    for name, data in PREMIUM_EMOJIS.items():
                        if data.get("id") == button_icon_id:
                            icon_emoji_name = name
                            break
                    
                    await update.message.reply_text(
                        f"✅ <b>{len(buttons)} button(s) added with premium emoji icons!</b>\n\n"
                        f"📊 <b>Preview above shows how message will look</b>\n"
                        f"🎨 <b>Button colors:</b>\n"
                        + "\n".join([f"  • {btn['text']} ({btn.get('color', 'primary').upper()})" for btn in buttons]) +
                        f"\n✨ <b>Premium emoji icon on buttons:</b> '{icon_emoji_name}' (from your text)\n"
                        f"\nNow send the channel username (with @)\n\n"
                        f"Example: @yourchannel\n\n"
                        f"⚠️ You must be admin in that channel",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Preview error: {e}")
                    await update.message.reply_text(f"❌ Error creating preview: {e}")
            else:
                await update.message.reply_text(
                    "Now send the channel username (with @)\n\n"
                    "Example: @yourchannel\n\n"
                    "⚠️ You must be admin in that channel"
                )
        else:
            await update.message.reply_text(
                "Send /addbutton to add more buttons\n"
                "Or send /donebuttons to finish"
            )
    
    elif step == "waiting_channel2":
        channel = update.message.text.strip()
        
        if not channel.startswith("@"):
            error_emoji = get_emoji_html("crying")
            await update.message.reply_text(
                f"{error_emoji} Please send channel username starting with @\n"
                "Example: @yourchannel",
                parse_mode="HTML"
            )
            return
        
        is_admin = await is_admin_in_channel(context, user_id, channel)
        
        if not is_admin:
            error_emoji = get_emoji_html("crying")
            await update.message.reply_text(
                f"{error_emoji} Access Denied!\n\n"
                f"You are not an admin in {channel}\n"
                "Only channel admins can broadcast messages.\n\n"
                "Make sure:\n"
                "1. You are admin in the channel\n"
                "2. Bot is admin in the channel\n"
                "3. Channel username is correct",
                parse_mode="HTML"
            )
            del user_data_store[user_id]
            return
        
        user_data_store[user_id]["channel"] = channel
        
        buttons = user_data_store[user_id].get("buttons", [])
        original_text = user_data_store[user_id].get("original_text", "")
        button_icon_id = get_emoji_id_from_text(original_text)
        reply_markup = None
        
        if buttons:
            keyboard = []
            for btn in buttons:
                btn_color = btn.get("color", "primary")
                
                # ✅ CLEAN BUTTON TEXT IF PREMIUM ICON WILL BE ADDED
                button_text = btn["text"]
                if button_icon_id:
                    button_text = strip_emojis(button_text)
                
                button_dict = {
                    "text": button_text
                }
                
                if btn.get("type") == "url":
                    button_dict["url"] = btn["url"]
                else:
                    button_dict["callback_data"] = f"copy_{btn.get('copy_text', '')[:50]}"
                
                button_dict["style"] = btn_color
                if button_icon_id:
                    button_dict["icon_custom_emoji_id"] = button_icon_id
                
                keyboard.append([InlineKeyboardButton(**button_dict)])
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        if user_data_store[user_id].get("is_photo"):
            caption = convert_normal_emojis_to_premium(user_data_store[user_id].get("caption", ""))
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=user_data_store[user_id]["photo_file_id"],
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        else:
            text = convert_normal_emojis_to_premium(user_data_store[user_id].get("text", ""))
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        
        verified = get_emoji_html("heart")
        await update.message.reply_text(
            f"{verified} Final Preview with Buttons ↑\n\n"
            f"📢 Channel: {channel}\n"
            f"👑 Your Status: Admin ✓\n"
            f"📎 Buttons: {len(buttons)}\n\n"
            f"✅ Send CONFIRM to broadcast\n"
            f"❌ Send CANCEL to abort",
            parse_mode="HTML",
            reply_markup=await confirm_cancel_kb()
        )
        user_data_store[user_id]["step"] = "confirm2"
    
    elif step == "confirm2":
        response = update.message.text.upper() if update.message.text else ""
        
        if response == "CONFIRM":
            try:
                channel = user_data_store[user_id]["channel"]
                is_photo = user_data_store[user_id].get("is_photo", False)
                buttons = user_data_store[user_id].get("buttons", [])
                original_text = user_data_store[user_id].get("original_text", "")
                button_icon_id = get_emoji_id_from_text(original_text)
                
                is_admin = await is_admin_in_channel(context, user_id, channel)
                
                if not is_admin:
                    error_emoji = get_emoji_html("crying")
                    await update.message.reply_text(
                        f"{error_emoji} Access Revoked!\n\n"
                        f"You are no longer admin in {channel}\n"
                        "Broadcast cancelled.",
                        parse_mode="HTML"
                    )
                    del user_data_store[user_id]
                    return
                
                reply_markup = None
                if buttons:
                    keyboard = []
                    for btn in buttons:
                        btn_color = btn.get("color", "primary")
                        
                        # ✅ CLEAN BUTTON TEXT IF PREMIUM ICON WILL BE ADDED
                        button_text = btn["text"]
                        if button_icon_id:
                            button_text = strip_emojis(button_text)
                        
                        button_dict = {
                            "text": button_text
                        }
                        
                        if btn.get("type") == "url":
                            button_dict["url"] = btn["url"]
                        else:
                            button_dict["callback_data"] = f"copy_{btn.get('copy_text', '')[:50]}"
                        
                        button_dict["style"] = btn_color
                        if button_icon_id:
                            button_dict["icon_custom_emoji_id"] = button_icon_id
                        
                        keyboard.append([InlineKeyboardButton(**button_dict)])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                
                if is_photo:
                    caption = convert_normal_emojis_to_premium(user_data_store[user_id].get("caption", ""))
                    await context.bot.send_photo(
                        chat_id=channel,
                        photo=user_data_store[user_id]["photo_file_id"],
                        caption=caption,
                        parse_mode="HTML",
                        reply_markup=reply_markup,
                        disable_notification=True
                    )
                else:
                    text = convert_normal_emojis_to_premium(user_data_store[user_id].get("text", ""))
                    await context.bot.send_message(
                        chat_id=channel,
                        text=text,
                        parse_mode="HTML",
                        reply_markup=reply_markup,
                        disable_notification=True
                    )
                
                # Get emoji name for display
                icon_emoji_name = "verified"
                for name, data in PREMIUM_EMOJIS.items():
                    if data.get("id") == button_icon_id:
                        icon_emoji_name = name
                        break
                
                success_emoji = get_emoji_html("heart")
                await update.message.reply_text(
                    f"{success_emoji} Broadcast 2.0 successful!\n\n"
                    f"📢 Sent to: {channel}\n"
                    f"👑 Broadcast by: Admin\n"
                    f"📎 Buttons added: {len(buttons)}\n"
                    f"✨ Premium emoji icon on buttons: '{icon_emoji_name}' (from your text mapping)\n"
                    f"✨ All normal emojis converted to premium!\n"
                    f"Use /broadcast2 for another broadcast",
                    parse_mode="HTML"
                )
                
            except Exception as e:
                error_emoji = get_emoji_html("crying")
                await update.message.reply_text(
                    f"{error_emoji} Error: {str(e)}\n\n"
                    f"Make sure:\n"
                    f"1. Bot is admin in {channel}\n"
                    f"2. Bot can send messages in channel\n"
                    f"3. Try again with /broadcast2"
                )
            
            del user_data_store[user_id]
        
        elif response == "CANCEL":
            del user_data_store[user_id]
            cancel_emoji = get_emoji_html("crying")
            await update.message.reply_text(f"{cancel_emoji} Broadcast cancelled", parse_mode="HTML")

def main():
    load_emojis() 
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ads", ads_command))
    application.add_handler(CommandHandler("ads1", ads1_command))
    application.add_handler(CommandHandler("ads2", ads2_command))
    application.add_handler(CommandHandler("ads3", ads3_command))
    application.add_handler(CommandHandler("ads4", ads4_command))
    application.add_handler(CommandHandler("myemojis", myemojis_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("broadcast2", broadcast2_command))
    application.add_handler(CommandHandler("addemoji", addemoji_command))
    application.add_handler(CommandHandler("addemojilink", addemojilink_command))
    application.add_handler(CommandHandler("addemoji2", addemoji2_command))
    application.add_handler(CommandHandler("addbutton", handle_message))
    application.add_handler(CommandHandler("donebuttons", handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    
    print("Bot is starting... Press Ctrl+C to stop.")
    print(f"Loaded {len(PREMIUM_EMOJIS)} premium emojis")
    print("Commands: /start, /ads, /ads1-4, /myemojis, /help, /broadcast, /broadcast2, /addemoji, /addemojilink, /addemoji2")
    print("Broadcast2: Text messages, Photos with captions, all formatting preserved + BUTTONS with colors!")
    print("✨ NEW: Premium emoji icons on buttons - automatically mapped from your text!")
    print("  Priority: 1st mapping (exact match) → 2nd mapping (similar) → 3rd mapping (first system emoji)")
    print("Button colors available: Blue (primary), Green (success), Red (danger)")
    print("Use /addbutton to add more buttons, /donebuttons to finish")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

## WHO USED THIS SOURCE FOR OWN WAY AND DONT GIVE CREDIT HE SHE IS GAY AND MY SON 
# CREDIT - @PROVIDERBOTZ