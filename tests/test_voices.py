import httpx

from plapperi import Dialect, Plapperi, Voice, VoiceGender
from plapperi.operations.voices.client import VoicesClient


VOICE_PAYLOAD = {
    "voices": [
        {
            "id": "alba",
            "name": "Alba",
            "gender": "female",
            "supportedDialects": ["be", "gr", "lu", "zh"],
        },
        {
            "id": "calder",
            "name": "Calder",
            "gender": "male",
            "supportedDialects": ["be", "gr", "lu", "zh"],
        },
    ]
}


def test_main_client_exposes_voices_operations():
    client = Plapperi(api_key="secret")
    try:
        assert isinstance(client.voices, VoicesClient)
    finally:
        client.close()


def test_list_voices_sends_api_key_and_parses_typed_catalog():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["authorization"] = request.headers.get("Authorization")
        return httpx.Response(200, json=VOICE_PAYLOAD)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = VoicesClient("https://api.example", "secret", http_client)
        voices = client.list()

    assert captured == {
        "method": "GET",
        "path": "/voices",
        "authorization": "ApiKey secret",
    }
    assert [voice.id for voice in voices] == ["alba", "calder"]
    assert all(isinstance(voice, Voice) for voice in voices)
    assert voices[0].gender is VoiceGender.FEMALE
    assert voices[1].gender is VoiceGender.MALE
    assert voices[0].supported_dialects == [
        Dialect.BERN,
        Dialect.GRAUBUNDEN,
        Dialect.LUCERNE,
        Dialect.ZURICH,
    ]
