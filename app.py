class App:
    async def __call__(self, scope, revieve, send):
        if scope['type'] == 'http':
            await send({
                "type":   "http.response.start",
                "status": 200,
                "headers": [
                    [
                        b"content-type",
                        b"text/plain"
                     ],
                ]
            })
            await send({
                "type": "http.response.body",
                "body": b"Hello from Taipan!"
            })
        if scope['type'] == 'lifespan':
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers" : [
                    [
                        b"content-type",
                        b"text/plain"
                    ]
                ]
            })
            await send({
                "type": "http.reponse.body",
                "body": b"Taipan Server was started!"
            })