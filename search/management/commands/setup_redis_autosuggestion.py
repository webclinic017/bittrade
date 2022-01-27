from django.core.management.base import BaseCommand
import redis
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition
from redis.commands.search.suggestion import Suggestion
import json
from django.contrib.auth.models import User
from kiteconnect import KiteConnect


class Command(BaseCommand):
    help = "Setup's the autosuggestion index in redis"

    def handle(self, *args, **options):
        r = redis.Redis()
        self.stdout.write(self.style.SUCCESS(
            'Connected to redis'))

        try:
            r.ft("instrument_idx").dropindex(delete_documents=True)
            self.stdout.write(self.style.SUCCESS(
                'Deleting if index already exists'))
        except Exception:
            pass

        index_defination = IndexDefinition(prefix=["instrument:"])

        schema = (
            TextField("tradingsymbol"),
            TextField("expiry"),
            TextField("instrument_type"),
            TextField("exchange"),
            NumericField("instrument_token"),
            NumericField("lot_size")
        )

        r.ft("instrument_idx").create_index(schema, index_defination)

        user = User.objects.get(username="admin").userprofile

        kite = KiteConnect(user.api_key, user.access_token)
        instruments = kite.instruments()

        self.stdout.write(self.style.SUCCESS(
            'Successfully fetched instruments'))

        instruments = list(
            map(
                lambda x: {
                    "tradingsymbol": x["tradingsymbol"],
                    "expiry": str(x["expiry"]),
                    "instrument_type": x["instrument_type"],
                    "exchange": x["exchange"],
                    "instrument_token": x["instrument_token"],
                    "lot_size": x["lot_size"]
                },
                instruments,
            )
        )

        data = instruments

        for document in data:
            r.hset(f"instrument:{document['tradingsymbol']}", mapping=document)
            r.ft("instrument_idx").sugadd(
                "tradingsymbol", Suggestion(document["tradingsymbol"]))

        self.stdout.write(self.style.SUCCESS(
            'Successfully created the index for tickers'))
