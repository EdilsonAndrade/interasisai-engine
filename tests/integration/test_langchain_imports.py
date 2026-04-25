def test_langchain_packages_are_importable() -> None:
    import langchain
    import langchain_community  # noqa: F401
    import langchain_core  # noqa: F401
    import langchain_google_genai  # noqa: F401

    assert langchain.__version__
