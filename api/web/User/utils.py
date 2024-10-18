from pydantic import BaseModel
from typing import Type

def generate_form_html(schema: Type[BaseModel]) -> str:
    form_html = ""
    for field_name, field in schema.__annotations__.items():
        form_html += f"""
        <div>
            <label for="{field_name}">{field_name.capitalize()}:</label>
            <input type="text" id="{field_name}" name="{field_name}" required>
        </div>
        """
    return form_html