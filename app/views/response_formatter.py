from flask import jsonify
from typing import Any, Dict, List, Optional


def success_response(data: Any = None, message: str = None, status_code: int = 200):
    if data is not None:
        if isinstance(data, dict):
            response = data.copy()
            if message:
                response['message'] = message
            return jsonify(response), status_code
        elif isinstance(data, list):
            response = {'data': data}
            if message:
                response['message'] = message
            return jsonify(response), status_code
        else:
            response = {'data': data}
            if message:
                response['message'] = message
            return jsonify(response), status_code
    else:
        response = {}
        if message:
            response['message'] = message
        return jsonify(response), status_code


def error_response(error: str, reason: str, module: str = "unknown", 
                   safe_for_demo: bool = True, diagnostics: Optional[Dict] = None, 
                   status_code: int = 400):
    response = {
        "error": error,
        "reason": reason,
        "module": module,
        "safe_for_demo": safe_for_demo
    }
    if diagnostics:
        response["diagnostics"] = diagnostics
    return jsonify(response), status_code


def validation_error_response(errors: List[Dict]):
    return jsonify({
        "error": "Invalid input",
        "reason": "Request data validation failed",
        "module": "validation",
        "safe_for_demo": True,
        "errors": errors
    }), 400

