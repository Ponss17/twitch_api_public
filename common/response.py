from flask import Response

def text_response(body: str, status: int = 200):
    return Response(body, content_type='text/plain; charset=utf-8', status=status)