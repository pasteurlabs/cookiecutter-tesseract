from pydantic import BaseModel
from tesseract_core.runtime import Array, Float32

# Ensure we can import shared code
# Reminder: project slug is test_project
from test_project_shared import foobar


class InputSchema(BaseModel):
    """InputSchema of the Tesseract, accepts a vector and a scalar."""

    vector: Array[(None,), Float32]
    scale_factor: Float32


class OutputSchema(BaseModel):
    """Returns scaled vector."""

    scaled_vector: Array[(None,), Float32]


def apply(inputs: InputSchema) -> OutputSchema:
    """Execute the Tesseract."""
    assert foobar() is True
    return OutputSchema(scaled_vector=inputs.vector * inputs.scale_factor)
