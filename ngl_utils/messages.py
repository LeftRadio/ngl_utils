import sys

# ------------------------------------------------------------------------------
# parseICO
# ------------------------------------------------------------------------------
def _format(msg, left_margin=0, right_margin=120):
    """ Format a message by inserting line breaks at appropriate places.  msg
    is the text of the message.  left_margin is the position of the left
    margin.  right_margin is the position of the right margin.  Returns the
    formatted message.
    """

    curs = left_margin
    fmsg = " " * left_margin

    for w in msg.split():
        l = len(w)
        if curs != left_margin and curs + l > right_margin:
            fmsg = fmsg + "\n" + (" " * left_margin)
            curs = left_margin

        if curs > left_margin:
            fmsg = fmsg + " "
            curs = curs + 1

        fmsg = fmsg + w
        curs = curs + l

    return fmsg

# ------------------------------------------------------------------------------
# error message
# ------------------------------------------------------------------------------
def error(msg):
    """ Display an error message and terminate.  msg is the text of the error
    message.
    """
    msg = str(msg)
    sys.stderr.write(_format("Error: " + msg) + "\n")
    sys.exit(True)

# ------------------------------------------------------------------------------
# inform message
# ------------------------------------------------------------------------------
def inform(msg):
    """ Display an information message.  msg is the text of the error message.
    """
    msg = str(msg)
    sys.stdout.write(_format("Inform: " + msg) + "\n")

# ------------------------------------------------------------------------------
# inform message
# ------------------------------------------------------------------------------
def newline():
    sys.stdout.write("\n")