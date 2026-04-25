from presentation.schemas import (
    ChatAudioSchema,
    ChatMessageSchema,
    ChatMetadataSchema,
    ChatProcessResponseSchema,
    ConsultRequestSchema,
    ConsultResponseSchema,
)


_MIN_DESCRIPTION_LENGTH = 10


def _all_descriptions_present(model_cls) -> bool:
    return all(
        field.description and len(field.description.strip()) >= _MIN_DESCRIPTION_LENGTH
        for field in model_cls.model_fields.values()
    )


def test_consult_request_schema_fields_have_descriptions() -> None:
    assert _all_descriptions_present(ConsultRequestSchema)


def test_consult_response_schema_fields_have_descriptions() -> None:
    assert _all_descriptions_present(ConsultResponseSchema)


def test_chat_audio_schema_fields_have_descriptions() -> None:
    assert _all_descriptions_present(ChatAudioSchema)


def test_chat_message_schema_fields_have_descriptions() -> None:
    assert _all_descriptions_present(ChatMessageSchema)


def test_chat_metadata_schema_fields_have_descriptions() -> None:
    assert _all_descriptions_present(ChatMetadataSchema)


def test_chat_process_response_schema_fields_have_descriptions() -> None:
    assert _all_descriptions_present(ChatProcessResponseSchema)
