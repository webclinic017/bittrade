import redis


class RedisInstrumentSearch:
    __redis_instance: redis.Redis = None

    @staticmethod
    def is_redis_connected():
        try:
            RedisInstrumentSearch.__redis_instance.ping()
        except Exception:
            return False

        return True

    @staticmethod
    def get_redis_instance():
        if RedisInstrumentSearch.__redis_instance == None or not RedisInstrumentSearch.is_redis_connected():
            RedisInstrumentSearch.__redis_instance = redis.Redis(
                decode_responses=True)

            print('[*] returning new connection to redis ....')
            return RedisInstrumentSearch.__redis_instance

        return RedisInstrumentSearch.__redis_instance

    def get_suggestions(self, search):
        r = RedisInstrumentSearch.get_redis_instance()

        for suggestion in r.ft("instrument_idx").sugget("tradingsymbol", search):
            yield r.hgetall("instrument:" + suggestion.string)
