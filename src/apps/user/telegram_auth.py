import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
from urllib import parse
from urllib.parse import unquote
from uuid import UUID

from django.conf import settings

from apps.user.models import User


@dataclass
class TelegramData:
    @dataclass
    class TelegramUser:
        id: int
        first_name: str
        last_name: str
        username: str | None
        language_code: str
        allows_write_to_pm: bool

    user: TelegramUser
    auth_date: datetime
    hash: str


class TelegramAuthVariant:
    def __init__(self, init_data: str):
        self._init_data = init_data

    def auth(self) -> User:
        token_data = self._get_data_from_telegram_token()

        user_id = str(token_data.user.id)
        user, is_created = User.objects.get_or_create(
            username=user_id,
            defaults={
                'first_name': token_data.user.first_name.strip(),
                'last_name': (token_data.user.last_name or token_data.user.username or '').strip(),
            }
        )
        if not is_created:
            updated = False
            if user.first_name != token_data.user.first_name.strip():
                user.first_name = token_data.user.first_name.strip()
                updated = True
            if user.last_name != (token_data.user.last_name or token_data.user.username or '').strip():
                user.last_name = (token_data.user.last_name or token_data.user.username or '').strip()
                updated = True
            if updated:
                user.save()
        return user

    def _get_data_from_telegram_token(self) -> TelegramData:
        self._check_telegram_init_data(settings.BOT_TOKEN)
        telegram_data = parse.parse_qs(parse.urlsplit("?" + self._init_data).query)
        self._check_if_telegram_data_expired(telegram_data)
        user = json.loads(telegram_data["user"][0])
        tg_data = TelegramData(
            user=TelegramData.TelegramUser(
                id=user["id"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                username=user.get("username"),
                language_code=user["language_code"],
                allows_write_to_pm=user["allows_write_to_pm"],
            ),
            auth_date=datetime.fromtimestamp(int(telegram_data["auth_date"][0])),
            hash=telegram_data["hash"][0],
        )
        return tg_data

    def _check_telegram_init_data(self, bot_token: str) -> None:
        init_data = unquote(self._init_data)
        data_check_arr = init_data.split('&')
        needle = 'hash='
        hash_item = ''
        telegram_hash = ''
        for item in data_check_arr:
            if item[0:len(needle)] == needle:
                telegram_hash = item[len(needle):]
                hash_item = item
        data_check_arr.remove(hash_item)
        data_check_arr.sort()
        data_check_string = "\n".join(data_check_arr)
        secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if calculated_hash != telegram_hash:
            raise ValueError('Invalid Telegram init data')

    @classmethod
    def _check_if_telegram_data_expired(cls, telegram_data: dict) -> None:
        expired_at = datetime.now(UTC) - timedelta(seconds=60)
        if int(telegram_data["auth_date"][-1]) < expired_at.timestamp():
            raise ValueError('Telegram init data has expired')
