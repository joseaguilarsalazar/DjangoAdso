import redis

def test_redis_connection(host='localhost', port=6379, password=None, db=0):
    try:
        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True
        )
        # Test connection with PING
        pong = r.ping()
        if pong:
            print("✅ Connected to Redis!")
        else:
            print("❌ Failed to connect.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Change host/port/password to match your Redis service
    test_redis_connection(host="94.130.228.35", port=6379, password='1234')
