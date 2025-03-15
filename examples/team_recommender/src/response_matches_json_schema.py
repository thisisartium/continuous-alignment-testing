from jsonschema import FormatChecker, validate

blank_checker = FormatChecker()


def response_matches_json_schema(
    response: str,
    schema: any,
    format_checker: FormatChecker = blank_checker,
) -> bool:
    """
        Validates if a given response matches the provided JSON schema.

    :return:
    :param response: The response JSON data as a string.
    :param schema: The schema to validate against.
    :param format_checker: The format checker to use.
    :return: True if the response matches the schema, otherwise False.
    :type format_checker: FormatChecker
    """
    try:
        validate(instance=response, schema=schema, format_checker=format_checker)
        return True
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
