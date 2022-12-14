from requests import get, Response, exceptions


def fetch_web_data(in_url: str) -> Response:
    """A safe way to fetch a web page

    Args:
        in_url (str): A url of the webpage to be fetched

    Raises:
        SystemExit: Exits program if requests error

    Returns:
        Response: A response object carrying the webpage requested
    """
    try:
        response = get(url=in_url, timeout=10)
    except exceptions.RequestException as error:
        raise SystemExit(error)
    return response
