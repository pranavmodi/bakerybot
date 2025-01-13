from fastapi import Request, HTTPException
from fastapi.responses import Response, JSONResponse
from app.config.settings import INPUT_FORMAT
import json
import logging

logger = logging.getLogger(__name__)

class ResponseService:
    def create_twilio_response(self, message: str) -> str:
        """Create a TwiML response for Twilio."""
        # Escape any XML special characters in the message
        message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""

    async def extract_message(self, request: Request) -> str:
        """Extract message from request based on input format."""
        if INPUT_FORMAT == "form":
            try:
                form_data = await request.form()
                message = form_data.get('Body', '')
                logger.info(f"Form data received: {dict(form_data)}")
                return message
            except Exception as e:
                logger.error(f"Error parsing form data: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error processing form data: {str(e)}")
        else:  # json format
            try:
                data = await request.json()
                logger.info(f"JSON data received: {json.dumps(data, indent=2)}")
                return data.get('message', '')
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")

    def create_response(self, response_text: str) -> Response:
        """Create appropriate response based on input format."""
        if INPUT_FORMAT == "form":
            twiml_response = self.create_twilio_response(response_text)
            return Response(
                content=twiml_response,
                media_type="text/xml",
                headers={"Cache-Control": "no-cache"}
            )
        else:
            return JSONResponse(content={
                "response": response_text
            })

    def create_error_response(self, error_message: str, status_code: int = 400) -> Response:
        """Create error response based on input format."""
        if INPUT_FORMAT == "form":
            twiml_response = self.create_twilio_response(error_message)
            return Response(
                content=twiml_response,
                media_type="text/xml",
                status_code=status_code,
                headers={"Cache-Control": "no-cache"}
            )
        else:
            raise HTTPException(status_code=status_code, detail=error_message) 