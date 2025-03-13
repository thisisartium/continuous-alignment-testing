import logging
import sys
from typing import Optional

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.trace.span import Span


class OpenTelemetryLogHandler(logging.Handler):
    """
    A custom logging handler that forwards log records to OpenTelemetry as span events.

    This bridges the gap between the venerable logging module (circa 2002)
    and modern distributed tracing (circa 2019+).
    """

    def __init__(self, level=logging.NOTSET, add_span_attributes: bool = True):
        super().__init__(level)
        self.add_span_attributes = add_span_attributes
        self.tracer = trace.get_tracer(__name__)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Convert a LogRecord to an OpenTelemetry span event.
        """
        try:
            # Get the current active span, if available
            current_span: Span = trace.get_current_span()

            # Skip if no active span and we're not in a traced context
            if not current_span or not current_span.is_recording():
                return

            # Extract relevant info from log record
            attributes = {}
            if self.add_span_attributes:
                attributes = {
                    "log.level": record.levelname,
                    "log.logger": record.name,
                    "log.thread": record.threadName,
                    "log.file.name": record.filename,
                    "log.function": record.funcName,
                    "log.line": record.lineno,
                }

                # Add any extra attributes from the record
                if hasattr(record, "otel_attributes"):
                    attributes.update(record.otel_attributes)

            # Format the message
            self.format(record)

            # Add event to the current span
            current_span.add_event(name=f"log.{record.levelname.lower()}", attributes=attributes)

            # For errors, add exception info if available
            if record.exc_info and record.levelno >= logging.ERROR:
                exception_type, exception_value, _ = record.exc_info
                current_span.record_exception(
                    exception=exception_value,
                    attributes={
                        "exception.type": exception_type.__name__,
                        "exception.message": str(exception_value),
                    },
                )

        except Exception:
            # Never let an error in our handler cause application issues
            # This is a cardinal rule of logging handlers - fail silently
            self.handleError(record)


def configure_logger_for_opentelemetry(logger_name: Optional[str] = None) -> logging.Logger:
    """Configure a logger to send events to OpenTelemetry."""
    # Get logger
    logger = logging.getLogger(logger_name)

    # Create and add OpenTelemetry handler
    otel_handler = OpenTelemetryLogHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    otel_handler.setFormatter(formatter)
    logger.addHandler(otel_handler)

    # You can keep console output for local development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set level
    logger.setLevel(logging.INFO)

    return logger


# Example usage
if __name__ == "__main__":
    # Configure OpenTelemetry

    # Configure logger
    logger = configure_logger_for_opentelemetry("example.app")

    # Create a simple trace with logging inside
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("example-operation") as span:
        # These logs will now show up as events in the span
        logger.info("Starting operation")

        # You can add custom OpenTelemetry attributes to log records
        extra = {"otel_attributes": {"custom.dimension": "some-value"}}
        logger.info("Processing item 42", extra=extra)

        try:
            # Simulate an error
            result = 1 / 0
        except Exception:
            logger.exception("Operation failed")

        logger.info("Operation completed")
