import json
from io import BytesIO
import base64
from barcode import ITF
from barcode.writer import ImageWriter

MM_TO_POINTS = 2.834645669291339

def line_to_barcode(line: str) -> str:
    """
    Converts a 47-character digit line into an ITF barcode string.
    """
    sanitized_line = line.replace(' ', '').replace('.', '')
    if len(sanitized_line) != 47:
        raise ValueError("The digit line must have exactly 47 characters.")
    
    return (
        sanitized_line[0:4] + sanitized_line[32:47] +
        sanitized_line[4:9] + sanitized_line[10:20] + sanitized_line[21:31]
    )

def generate_barcode_base64(barcode_data: str) -> str:
    """
    Generates an ITF barcode image and returns its base64 representation.
    """
    buffer = BytesIO()
    barcode = ITF(barcode_data, writer=ImageWriter())
    barcode.write(
        buffer,
        options={
            "module_width": 0.13 * MM_TO_POINTS,
            "module_height": 13 * MM_TO_POINTS,
            "write_text": False,
        },
    )
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def get_barcode(event, context):
    """
    Serverless handler for generating a barcode from a digit line.
    """
    line = event.get("queryStringParameters", {}).get("line")

    if not line:
        return create_response(400, success=False, message="The 'line' parameter is missing.")
    
    try:
        barcode_data = line_to_barcode(line)
        base64_image = generate_barcode_base64(barcode_data)
        return create_response(200, success=True, data={"base_64": base64_image})
    except ValueError as ve:
        return create_response(400, success=False, message=str(ve))
    except Exception as e:
        return create_response(500, success=False, message=f"Internal error: {str(e)}")

def create_response(status_code: int, success: bool, message: str = None, data: dict = None) -> dict:
    """
    Creates a formatted JSON HTTP response.
    """
    body = {"success": success}
    if message:
        body["message"] = message
    if data:
        body["data"] = data
    
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"}
    }
