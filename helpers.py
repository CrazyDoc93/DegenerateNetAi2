def chunks(lst, n):
    """
    Split a list into chunks of size n

    :param lst: the list to be chunked
    :param n: The number of items in the chunk
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
