from telethon import TelegramClient, events
import asyncio
import datetime
from flask import Flask
from threading import Thread

# ==== CONFIGURACIÓN ====
api_id = 12345678  # ← Reemplaza con tu API ID
api_hash = 'tu_api_hash'  # ← Reemplaza con tu API Hash
session_name = 'miarchivo.session'
grupo_logs = 'logsdelbotspammm'
ARCHIVO_GRUPOS = 'grupos.txt'
inicio = datetime.datetime.now()

client = TelegramClient(session_name, api_id, api_hash)

# ==== FLASK PARA UPTIME ROBOT ====
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot activo y escuchando órdenes."

def iniciar_web():
    app.run(host='0.0.0.0', port=8080)

# ==== FUNCIONES ====
def cargar_grupos():
    with open(ARCHIVO_GRUPOS, 'r') as f:
        return [line.strip() for line in f if line.strip()]

@client.on(events.NewMessage(from_users='me', pattern='/estado'))
async def estado(event):
    grupos = cargar_grupos()
    await event.reply(f"📦 {len(grupos)} grupos en grupos.txt\n🤖 Bot activo y escuchando.")

@client.on(events.NewMessage(from_users='me', pattern='/spam'))
async def spam(event):
    async for msg in client.iter_messages('me', limit=5):
        if msg.fwd_from:
            mensaje_origen = msg
            break
    else:
        await event.reply("⚠️ No encontré mensaje reenviado tuyo.")
        return

    grupos = cargar_grupos()
    if not grupos:
        await event.reply("⚠️ No hay grupos en el archivo.")
        return

    await event.reply(f"🚀 Enviando a {len(grupos)} grupos...")
    enviados_ok, enviados_fail = [], []

    for grupo in grupos:
        try:
            await client.send_message(grupo, mensaje_origen)
            enviados_ok.append(grupo)
            await asyncio.sleep(0.5)
        except Exception as e:
            enviados_fail.append(f"{grupo} → {e}")

    await event.reply(f"✅ Enviado a {len(enviados_ok)} grupos\n❌ Fallaron {len(enviados_fail)}")

    log_text = f"📤 LOG SPAM:\n✅ Correctos ({len(enviados_ok)}):\n" + \
               "\n".join(enviados_ok) + \
               f"\n\n❌ Fallidos ({len(enviados_fail)}):\n" + \
               "\n".join(enviados_fail) if enviados_fail else "\n(ninguno)"

    try:
        await client.send_message(grupo_logs, log_text)
    except Exception as e:
        print(f"❌ Error al enviar log: {e}")

@client.on(events.NewMessage(from_users='me', pattern=r'/test (.+)'))
async def test(event):
    grupo = event.pattern_match.group(1)
    try:
        await client.send_message(grupo, "🧪 Test de conexión.")
        await event.reply(f"✅ Enviado correctamente a {grupo}")
    except Exception as e:
        await event.reply(f"❌ Falló el envío a {grupo}\n{e}")

@client.on(events.NewMessage(from_users='me', pattern='/botinfo'))
async def botinfo(event):
    grupos = cargar_grupos()
    uptime = datetime.datetime.now() - inicio
    h, rem = divmod(uptime.seconds, 3600)
    m, s = divmod(rem, 60)
    await event.reply(f"🤖 Info del bot:\n📁 Grupos: {len(grupos)}\n⏱ Uptime: {h}h {m}m {s}s\n🌐 Online")

@client.on(events.NewMessage(from_users='me', pattern='/comandos'))
async def comandos(event):
    await event.reply(
        "📜 *Comandos disponibles:*\n\n"
        "🔹 /spam → Reenvía tu último mensaje reenviado a todos los grupos\n"
        "🔹 /estado → Muestra estado del bot\n"
        "🔹 /botinfo → Info técnica del bot\n"
        "🔹 /test @grupo → Prueba si puede enviar\n"
        "🔹 /comandos → Muestra esta lista\n"
        "🔹 /stats → Estadísticas actuales\n",
        parse_mode='Markdown'
    )

@client.on(events.NewMessage(from_users='me', pattern='/stats'))
async def stats(event):
    grupos = cargar_grupos()
    uptime = datetime.datetime.now() - inicio
    await event.reply(
        f"📊 Estadísticas:\n\n"
        f"🔹 Grupos cargados: {len(grupos)}\n"
        f"🔹 Tiempo encendido: {str(uptime).split('.')[0]}"
    )

# ==== INICIO ====
async def iniciar_telegram():
    await client.start()
    print("✅ Cliente Telegram iniciado.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    Thread(target=iniciar_web).start()
    asyncio.run(iniciar_telegram())
