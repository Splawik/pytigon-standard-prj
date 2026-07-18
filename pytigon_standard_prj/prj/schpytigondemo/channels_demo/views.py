from pytigon_lib.schviews.viewtools import dict_to_template


@dict_to_template("channels_demo/v_clock.html")
def clock(request, **argv):
    """
    Render the real-time clock demo page.

    Returns an empty context dict that is rendered via the channels_demo
    clock template, which uses a WebSocket channel to display a live clock.
    """

    return {}


@dict_to_template("channels_demo/v_openai.html")
def openai(request, **argv):
    """
    Render the OpenAI chat demo page.

    Returns an empty context dict rendered via the channels_demo OpenAI
    template, which uses a WebSocket channel for streaming AI chat.
    """

    return {}


@dict_to_template("channels_demo/v_ollama_ai.html")
def ollama_ai(request, **argv):
    """
    Render the Ollama AI chat demo page.

    Returns an empty context dict rendered via the channels_demo Ollama AI
    template, which uses a WebSocket channel for streaming local LLM chat.
    """

    return {}
