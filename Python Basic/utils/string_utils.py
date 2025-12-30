def is_palindrome(s):
    """
    Check if the given string is a palindrome.

    :param s: Input string to check
    :return: True if the string is a palindrome, False otherwise
    """
    # Remove spaces and convert to lowercase for uniformity
    cleaned_string = ''.join(s.split()).lower()
    # Compare the string with its reverse
    return cleaned_string == cleaned_string[::-1]