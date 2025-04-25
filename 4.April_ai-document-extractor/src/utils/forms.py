from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional

class ConfigOptionsForm(FlaskForm):
    """Form for configuring options for document processing."""
    
    # Dropdown for table handling options
    table_handling = SelectField(
        "Table Handling",
        choices=[
            ("keep", "Keep Original Table"),
            ("empty", "Convert to Empty Table"),
            ("remove", "Remove Tables")
        ],
        validators=[DataRequired()]
    )
    
    # Text area for field mapping
    field_mapping = TextAreaField(
        "Field Mapping (e.g., JSON or key-value pairs)",
        validators=[Optional()],
        description="Specify how fields in the original document map to fields in the output document."
    )
    
    # Input for custom placeholder text
    placeholder_text = StringField(
        "Custom Placeholder Text",
        validators=[Optional()],
        description="Specify placeholder text for empty fields in the output document."
    )
    
    # Page range selection
    page_range = StringField(
        "Page Range (e.g., 1-3, all)",
        validators=[Optional()],
        description="Specify which pages of the document should be processed."
    )
    
    # Dropdown for output formatting options
    output_formatting = SelectField(
        "Output Formatting",
        choices=[
            ("original", "Keep Original Formatting"),
            ("default", "Apply Default Formatting"),
            ("custom", "Custom Formatting")
        ],
        validators=[DataRequired()]
    )
    
    # Additional notes or instructions
    additional_notes = TextAreaField(
        "Additional Notes/Instructions",
        validators=[Optional()],
        description="Provide any additional instructions for the conversion process."
    )
    
    # Submit button
    submit = SubmitField("Submit")