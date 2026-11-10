from src.main import pipe_line


def test_pipe_format():
    record = {
        "anzahl": "2",
        "wortart": "Verb",
        "grundform": "rogare",
        "mittelspalte": "rogo, rogavi, rogatum",
        "perfektstamm": "rogav",
        "uebersetzung": "fragen",
        "klasse": "a",
        "wortstamm": "roga",
    }
    assert pipe_line(record) == "|2|Verb|rogare|rogo, rogavi, rogatum|rogav|fragen|a|roga|"
