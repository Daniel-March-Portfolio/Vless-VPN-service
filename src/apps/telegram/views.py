import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telebot.types import Message, Update, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from apps.balance.models import BalanceHistory
from apps.telegram.bot import bot
from apps.telegram.models import TelegramPayment
from apps.user.models import User


@bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout_query_handler(query: PreCheckoutQuery):
    user, _ = User.objects.get_or_create(
        username=str(query.from_user.id),
        defaults={
            'first_name': query.from_user.first_name.strip(),
            'last_name': (query.from_user.last_name or query.from_user.username or '').strip(),
        }
    )
    telegram_payment = TelegramPayment.objects.get(user=user, id=query.invoice_payload)
    if telegram_payment.transaction_id is None:
        bot.answer_pre_checkout_query(
            pre_checkout_query_id=query.id,
            ok=True
        )
    else:
        bot.answer_pre_checkout_query(
            pre_checkout_query_id=query.id,
            ok=False,
            error_message="Payment has already been processed."
        )

@bot.message_handler(func=lambda message: True, content_types=['successful_payment'])
def successful_payment_handler(message: Message):
    user = User.objects.get(username=str(message.from_user.id))
    BalanceHistory(
        user=user,
        amount=message.successful_payment.total_amount,
        description='Telegram payment',
    ).save()
    telegram_payment = TelegramPayment.objects.get(user=user, id=message.successful_payment.invoice_payload)
    telegram_payment.transaction_id = message.successful_payment.telegram_payment_charge_id
    telegram_payment.save()
    bot.delete_message(
        chat_id=message.chat.id,
        message_id=telegram_payment.message_id
    )

@bot.message_handler(commands=['start', 'menu'])
def menu_message_handler(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text='Work with the bot is done through the "*Menu*" button at the bottom of the screen.',
        parse_mode='Markdown',
    )

@bot.message_handler(commands=['admin'])
def menu_message_handler(message: Message):
    admin = User.objects.filter(username=str(message.from_user.id), is_superuser=True).first()
    if admin:
        reply_markup = InlineKeyboardMarkup()
        reply_markup.add(
            InlineKeyboardButton(text='Open', web_app=WebAppInfo(f'{settings.HOST}/auth/?as_admin=1'))
        )
        bot.send_message(
            chat_id=message.chat.id,
            text='Admin Panel:',
            reply_markup=reply_markup
        )


@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            json_str = request.body.decode('utf-8')
            update = Update.de_json(json.loads(json_str))
            bot.process_new_updates([update])
        except Exception as e:
            print(f"Telegram webhook error: {e}")
        return JsonResponse({"ok": True})
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)
