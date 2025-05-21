import os
from regula.facesdk.webclient import MatchImage, MatchRequest
from regula.facesdk.webclient.ext import FaceSdk
from regula.facesdk.webclient.gen.model.image_source import ImageSource

API_BASE_PATH = os.getenv("API_BASE_PATH", "https://faceapi.regulaforensics.com")

def compare_faces_sdk(document_photo_bytes: bytes, uploaded_photo_bytes: bytes) -> float:
    with FaceSdk(host=API_BASE_PATH) as sdk:
        images = [
            MatchImage(index=1, data=document_photo_bytes, type=ImageSource.DOCUMENT_RFID),
            MatchImage(index=2, data=uploaded_photo_bytes, type=ImageSource.LIVE)
        ]
        match_request = MatchRequest(images=images)
        match_response = sdk.match_api.match(match_request)

        if match_response.results:
            return match_response.results[0].similarity
        return 0.0
