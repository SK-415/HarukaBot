# 数据库上下文管理器
import redis
class RedisDB(object):
    'redis数据库的上下文管理器'
    def __init__(self, database = '0' ,host='127.0.0.1', port='6379',decode_responses=True):
        self.database = database
        self.host = host
        self.port = port
        self.decode_responses = decode_responses
        self.connection = None

    def __enter__(self):
        try:
            self.connection = redis.StrictRedis(host = self.host , port = self.port, db = self.database, decode_responses = self.decode_responses)
            return self.connection
        except Exception as ex:
            traceback.print_exc()  #traceback.print_exc()来代替print ex 来输出详细的异常信息
            raise ex

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 异常类型，异常值，异常追踪
        try:
            if not exc_type is None:
                pass
        except Exception as ex:
            traceback.print_exc()
            raise ex
        finally:
            self.connection.close()
if __name__ == '__main__':
    with RedisDB(2) as db:
        data = db.get('DedeUserID')
        print(data)