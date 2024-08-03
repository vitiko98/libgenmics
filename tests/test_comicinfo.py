from libgenmics import comicinfo


def test_make(tmp_path):
    comicinfo.make(
        tmp_path / "foo.xml", series="Foo Title", number="XD", languageiso="en"
    )
