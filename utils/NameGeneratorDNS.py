import uuid
import time


def generate_unique_dns_name(base_name: str, max_length: int = 63) -> str:
    """
    Generates a unique DNS name with a maximum length.

    Args:
        base_name: The base name for the DNS name.
        max_length: The maximum allowed length of the DNS name.

    Returns:
        A unique DNS name.
    """

    unique_id = uuid.uuid4().hex[:8]
    timestamp = int(time.time())
    base_name = base_name[:max_length - len(unique_id) - len(str(timestamp)) - 2]  # Adjust for separators
    dns_name = f"{base_name}-{unique_id}-{timestamp}"
    return dns_name[:max_length]
