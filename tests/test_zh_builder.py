from subtitleterms.deckbuilder.zh_builder import (
    HanEntry,
    ZH_Deck,
    tone_numbers_to_marks,
)


def zh_init():
    return {
        "张": HanEntry("张", "张的定义", 1, "zhang1"),
        "茵": HanEntry("茵", "茵的定义", 1, "yin1"),
    }


deck = ZH_Deck("zh-Hans", "en", zh_init)


def test_segment():
    answer = set(deck.segment(["我喜欢蛋糕。"]))
    for segment in ["我", "喜欢", "蛋糕"]:
        assert segment in answer
    assert "。" not in answer


def test_lookup_fallback():
    deck.entrystore.update_cache()
    a = deck.lookup_fallback("张茵")
    assert (a[0] == "张" and a[1] == "茵") or (a[0] == "茵" and a[1] == "张")


def test_tone_numbers_to_marks_umlaut():
    question = "情侶 情侣 [qing2 lu:3] /sweethearts/lovers/"
    expected = "情侶 情侣 [qíng lǚ] /sweethearts/lovers/"
    assert tone_numbers_to_marks(question) == expected


def test_tone_numbers_to_marks_location():
    # a<i a<o e<i ia< ia<o ie< io< iu< o<u ua< ua<i ue< ui< uo< ue<
    pairs = [
        (
            "介紹 介绍 [jie4 shao4] /to introduce (sb to sb)/to give a presentation/to present (sb for a job etc)/introduction/",
            "介紹 介绍 [jiè shào] /to introduce (sb to sb)/to give a presentation/to present (sb for a job etc)/introduction/",
        ),
        (
            "先睹為快 先睹为快 [xian1 du3 wei2 kuai4] /(idiom) to consider it a pleasure to be among the first to read (or watch or enjoy)/",
            "先睹為快 先睹为快 [xiān dǔ wéi kuài] /(idiom) to consider it a pleasure to be among the first to read (or watch or enjoy)/",
        ),
        (
            "千奇百怪 千奇百怪 [qian1 qi2 bai3 guai4] /fantastic oddities of every description (idiom)/",
            "千奇百怪 千奇百怪 [qiān qí bǎi guài] /fantastic oddities of every description (idiom)/",
        ),
        (
            "大熊座 大熊座 [Da4 xiong2 zuo4] /Ursa Major, the Great Bear (constellation)/",
            "大熊座 大熊座 [Dà xióng zuò] /Ursa Major, the Great Bear (constellation)/",
        ),
        (
            "富得流油 富得流油 [fu4 de5 liu2 you2] /affluent/very rich/",
            "富得流油 富得流油 [fù de liú yóu] /affluent/very rich/",
        ),
        (
            "工學院 工学院 [gong1 xue2 yuan4] /school of engineering/college of engineering/",
            "工學院 工学院 [gōng xué yuàn] /school of engineering/college of engineering/",
        ),
        (
            "奇詭 奇诡 [qi2 gui3] /strange; queer; intriguing/",
            "奇詭 奇诡 [qí guǐ] /strange; queer; intriguing/",
        ),
    ]
    for question, answer in pairs:
        assert tone_numbers_to_marks(question) == answer
