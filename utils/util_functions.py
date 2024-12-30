def is_int_between_0_and_10(text):
    try:
        # Try converting the text to an integer
        number = int(text)
        # Check if the number is within the range 0 to 10
        return 0 <= number <= 10
    except ValueError:
        # If conversion fails, it's not an integer
        return False


def is_less_5_words(text):
    words = text.split(',')
    if 0 <= len(words) <= 5:
        return True
    else:
        return False

