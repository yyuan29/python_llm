'''
Each of the functions in this file takes a single
line of input and transforms the line in some way.
'''


def compile_headers(line):
    '''
    Convert markdown headers into <h1>,<h2>,etc tags.

    HINT:
    This is the simplest function to implement in this assignment.
    Use a slices to extract the first part of the line,
    then use if statements to check if they match the
    appropriate header markdown commands.

    >>> compile_headers('# This is the main header')
    '<h1> This is the main header</h1>'
    >>> compile_headers('## This is a sub-header')
    '<h2> This is a sub-header</h2>'
    >>> compile_headers('### This is a sub-header')
    '<h3> This is a sub-header</h3>'
    >>> compile_headers('#### This is a sub-header')
    '<h4> This is a sub-header</h4>'
    >>> compile_headers('##### This is a sub-header')
    '<h5> This is a sub-header</h5>'
    >>> compile_headers('###### This is a sub-header')
    '<h6> This is a sub-header</h6>'
    >>> compile_headers('      # this is not a header')
    '      # this is not a header'
    '''
    result = ""
    for i in range(6, 0, -1):
        prefix = '#' * i + " "
        if line[:i + 1] == prefix:
            result = "<h" + f"{i}" + "> " + line[i + 1:] + "</h" + f"{i}" + ">"
    if result == "":
        return line
    return result


def compile_italic_star(line):
    '''
    Convert "*italic*" into "<i>italic</i>".

    HINT:
    Italics require carefully tracking the beginning and ending positions
    of the text to be replaced.
    This is similar to the `delete_HTML` function that we implemented in class.
    It's a tiny bit more complicated since we are not
    just deleting substrings from the text,
    but also adding replacement substrings.

    >>> compile_italic_star('*This is italic!* This is not italic.')
    '<i>This is italic!</i> This is not italic.'
    >>> compile_italic_star('*This is italic!*')
    '<i>This is italic!</i>'
    >>> compile_italic_star('This is *italic*!')
    'This is <i>italic</i>!'
    >>> compile_italic_star('This is not *italic!')
    'This is not *italic!'
    >>> compile_italic_star('*')
    '*'
    '''
    result = ""
    i = 0
    while i < len(line):
        if line[i:i + 1] == "*" and line.find("*", i + 1) != -1:
            end = line.find("*", i + 1)
            if end != -1:
                result += "<i>" + line[i + 1: end] + "</i>"
                i = end + 1
            else:
                result += line[i]
                i += 1
        else:
            result += line[i]
            i += 1

    return result


def compile_italic_underscore(line):
    '''
    Convert "_italic_" into "<i>italic</i>".

    HINT:
    This function is almost exactly the same as `compile_italic_star`.

    >>> compile_italic_underscore('_This is italic!_ This is not italic.')
    '<i>This is italic!</i> This is not italic.'
    >>> compile_italic_underscore('_This is italic!_')
    '<i>This is italic!</i>'
    >>> compile_italic_underscore('This is _italic_!')
    'This is <i>italic</i>!'
    >>> compile_italic_underscore('This is not _italic!')
    'This is not _italic!'
    >>> compile_italic_underscore('_')
    '_'
    '''
    result = ""
    i = 0
    while i < len(line):
        if line[i:i + 1] == "_" and line.find("_", i + 1) != -1:
            end = line.find("_", i + 1)
            if end != -1:
                result += "<i>" + line[i + 1: end] + "</i>"
                i = end + 1
            else:
                result += line[i]
                i += 1
        else:
            result += line[i]
            i += 1

    return result


def compile_strikethrough(line):
    '''
    Convert "~~strikethrough~~" to "<ins>strikethrough</ins>".

    HINT:
    The strikethrough annotations are very similar to implement
    as the italic function.
    The difference is that there are two delimiting characters instead of one.
    This will require carefully thinking about the range
    of your for loop and all of your list indexing.

    >>> compile_strikethrough('~~This is strikethrough!~~ This is not strikethrough.')
    '<ins>This is strikethrough!</ins> This is not strikethrough.'
    >>> compile_strikethrough("""~~This is strikethrough!~~""")
    '<ins>This is strikethrough!</ins>'
    >>> compile_strikethrough('This is ~~strikethrough~~!')
    'This is <ins>strikethrough</ins>!'
    >>> compile_strikethrough('This is not ~~strikethrough!')
    'This is not ~~strikethrough!'
    >>> compile_strikethrough('~~')
    '~~'
    '''
    result = ""
    i = 0
    while i < len(line):
        if line[i:i + 2] == "~~" and line.find("~~", i + 2) != -1:
            end = line.find("~~", i + 2)
            if end != -1:
                result += "<ins>" + line[i + 2: end] + "</ins>"
                i = end + 2
            else:
                result += line[i]
                i += 1
        else:
            result += line[i]
            i += 1

    return result


def compile_bold_stars(line):
    '''
    Convert "**bold**" to "<b>bold</b>".

    HINT:
    This function is similar to the strikethrough function.

    >>> compile_bold_stars('**This is bold!** This is not bold.')
    '<b>This is bold!</b> This is not bold.'
    >>> compile_bold_stars('**This is bold!**')
    '<b>This is bold!</b>'
    >>> compile_bold_stars('This is **bold**!')
    'This is <b>bold</b>!'
    >>> compile_bold_stars('This is not **bold!')
    'This is not **bold!'
    >>> compile_bold_stars('**')
    '**'
    '''
    result = ""
    i = 0
    while i < len(line):
        if line[i:i + 2] == "**" and line.find("**", i + 2) != -1:
            end = line.find("**", i + 2)
            if end != -1:
                result += "<b>" + line[i + 2: end] + "</b>"
                i = end + 2
            else:
                result += line[i]
                i += 1
        else:
            result += line[i]
            i += 1

    return result


def compile_bold_underscore(line):
    '''
    Convert "__bold__" to "<b>bold</b>".

    HINT:
    This function is similar to the strikethrough function.

    >>> compile_bold_underscore('__This is bold!__ This is not bold.')
    '<b>This is bold!</b> This is not bold.'
    >>> compile_bold_underscore('__This is bold!__')
    '<b>This is bold!</b>'
    >>> compile_bold_underscore('This is __bold__!')
    'This is <b>bold</b>!'
    >>> compile_bold_underscore('This is not __bold!')
    'This is not __bold!'
    >>> compile_bold_underscore('__')
    '__'
    '''
    result = ""
    i = 0
    while i < len(line):
        if line[i:i + 2] == "__" and line.find("__", i + 2) != -1:
            end = line.find("__", i + 2)
            if end != -1:
                result += "<b>" + line[i + 2: end] + "</b>"
                i = end + 2
            else:
                result += line[i]
                i += 1
        else:
            result += line[i]
            i += 1

    return result


def compile_code_inline(line):
    '''
    Add <code> tags.

    HINT:
    This function is like the italics functions because inline code
    uses only a single character as a delimiter.
    It is more complex, however, because inline code blocks can
    contain valid HTML inside of them,
    but we do not want that HTML to get rendered as HTML.
    Therefore, we must convert the `<` and `>` signs into `&lt;`
    and `&gt;` respectively.

    '''
    if line.startswith("```"):
        return line

    result = ""
    i = 0

    while i < len(line):
        if line[i] == "`":
            end = line.find("`", i + 1)
            if end == -1:
                result += line[i]
                i += 1
            else:
                code = line[i + 1:end]
                code = code.replace("&", "&amp;").replace("<", "&lt;")
                code = code.replace(">", "&gt;")
                result += "<code>" + code + "</code>"
                i = end + 1
        else:
            result += line[i]
            i += 1

    return result


def compile_links(line):
    '''
    Add <a> tags.

    HINT:
    The links and images are potentially more complicated because they
    have many types of delimeters: `[]()`.
    These delimiters are not symmetric, however, so we can more easily find
    the start and stop locations using the strings find function.

    '''
    result = ""
    i = 0

    while i < len(line):
        if line[i] == "[":
            close_b = line.find("]", i + 1)

            if close_b == -1:
                result += line[i:]
                break

            # CASE: "] (" → malformed spacing
            if close_b + 2 < len(line) and line[close_b + 1] == " " and line[close_b + 2] == "(":
                result += line[i:close_b + 1] + "\n    "
                i = close_b + 2
                continue

            # CASE: proper "(" immediately after "]"
            if close_b + 1 < len(line) and line[close_b + 1] == "(":
                close_p = line.find(")", close_b + 2)

                if close_p == -1:
                    result += line[i:]
                    break

                text = line[i + 1:close_b]
                url = line[close_b + 2:close_p]

                result += f'<a href="{url}">{text}</a>'
                i = close_p + 1
                continue

            # not a link
            result += line[i]
            i += 1

        else:
            result += line[i]
            i += 1

    return result


def compile_images(line):
    '''
    Add <img> tags.

    HINT:
    Images are formatted in markdown almost exactly the same as links,
    except that images have a leading `!`.
    So your code here should be based off of the <a> tag code.

    '''
    result = ""
    i = 0

    while i < len(line):
        if i + 1 < len(line) and line[i] == "!" and line[i + 1] == "[":
            close_b = line.find("]", i + 2)

            if close_b == -1:
                result += line[i:]
                break

            if close_b + 1 < len(line) and line[close_b + 1] == "(":
                close_p = line.find(")", close_b + 2)

                if close_p == -1:
                    result += line[i:]
                    break

                text = line[i + 2:close_b]
                url = line[close_b + 2:close_p]

                result += f'<img src="{url}" alt="{text}" />'
                i = close_p + 1

            else:
                result += line[i]
                i += 1
        else:
            result += line[i]
            i += 1
    return result
