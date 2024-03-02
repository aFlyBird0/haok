# 生成glm token

if __name__ == '__main__':
    import time
    import jwt


    def generate_token(apikey: str, exp_seconds: int):
        try:
            id, secret = apikey.split(".")
        except Exception as e:
            raise Exception("invalid apikey", e)

        payload = {
            "api_key": id,
            "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
            "timestamp": int(round(time.time() * 1000)),
        }

        return jwt.encode(
            payload,
            secret,
            algorithm="HS256",
            headers={"alg": "HS256", "sign_type": "SIGN"},
        )

    api_key = "629771279307558c5e82717fbe31b2dc.4AVoyNi7vM5N4xXl"
    exp_seconds = 60 * 60 * 24 * 90

    token = generate_token(api_key, exp_seconds)
    print(token)