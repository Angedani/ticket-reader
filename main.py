from telegram import Update
from telegram .ext import ApplicationBuilder, CommandHandler, MessageHandler,ContextTypes, filters
import easyocr
import re
from openpyxl import load_workbook
reader = easyocr.Reader(['en','es'], gpu = False)

ticket_Global = []
fecha_Global = ""

def es_precio(texto):
    return re.search(r'\d+[.,]\d{2}', texto)

def es_fecha(texto):
    return re.search(r'\d+[/]\d+[/]\d{4}',texto)

async def say_hello(update : Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello World!")

async def ticket(update : Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    await file.download_to_drive('Ticket.jpg')
    result = reader.readtext('Ticket.jpg' , detail = 0, width_ths = 20)
    lista = []
    for item in result:   
        if es_precio(item) != None:
            item1 = item.lower().title()
            lista.append(item1)
            
            print(item1)
            if 'TOTAL' in item.upper():
                break  
    for item in result:
        if es_fecha(item) != None:
            fecha = item[:10]
    global ticket_Global 
    ticket_Global= lista
    global fecha_Global 
    await update.message.reply_text("\n".join(lista))
    fecha_Global = fecha
    await update.message.reply_text(fecha_Global)
    

async def editar(update : Update, context: ContextTypes.DEFAULT_TYPE):
    global ticket_Global
    reply = update.message.reply_to_message
    if not reply or not reply.text:
        await update.message.reply_text(
            "Responde al mensaje del ticket y luego usa /editar"
        )
        return
    texto = reply.text
    ticket_Global = texto
    await update.message.reply_text("Ticket editado:\n" +ticket_Global)
    ticket_Global = ticket_Global.split("\n")
    await update.message.reply_text(ticket_Global)

async def editar_fecha(update : Update, context: ContextTypes.DEFAULT_TYPE):
    global ticket_Global
    reply = update.message.reply_to_message
    if not reply or not reply.text:
        await update.message.reply_text(
            "Responde al mensaje del ticket y luego usa /editarFecha"
        )
        return
    texto = reply.text
    fecha_Global = texto
    await update.message.reply_text("Fecha editada:\n" + fecha_Global)

async def guardar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    archivo = "Gastos1.xlsx"
    wb = load_workbook(archivo)
    ws = wb.active

    for item in ticket_Global[:-1]:
        concepto = item[:-4]
        cantidad = item[-4:] +"€"
        ws.append([fecha_Global,concepto,cantidad])

    wb.save(archivo)
    await update.message.reply_text("Guardado")

application = ApplicationBuilder().token("token").build()
application.add_handler(CommandHandler("start", say_hello))
application.add_handler(MessageHandler(filters.PHOTO, ticket))
application.add_handler(CommandHandler("editar", editar))
application.add_handler(CommandHandler("editarFecha", editar_fecha))
application.add_handler(CommandHandler("guardar", guardar))
application.run_polling(allowed_updates = Update.ALL_TYPES)
