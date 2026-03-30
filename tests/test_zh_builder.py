from subtitleterms.deckbuilder.zh_builder import tone_numbers_to_marks, tones


def test_tone_numbers_to_marks_umlaut():
    question = "情侶 情侣 [qing2 lu:3] /sweethearts/lovers/"
    answer = f"情侶 情侣 [qi{tones[2 - 1]}ng lu{tones[3 - 1]}] /sweethearts/lovers/"
    assert tone_numbers_to_marks(question) == answer


def test_tone_numbers_to_marks_location():
    # a<i a<o e<i ia< ia<o ie< io< iu< o<u ua< ua<i ue< ui< uo< ue<
    pairs = [
        (
            "介紹 介绍 [jie4 shao4] /to introduce (sb to sb)/to give a presentation/to present (sb for a job etc)/introduction/",
            f"介紹 介绍 [jie{tones[4 - 1]} sha{tones[4 - 1]}o] /to introduce (sb to sb)/to give a presentation/to present (sb for a job etc)/introduction/",
        ),
        (
            "先睹為快 先睹为快 [xian1 du3 wei2 kuai4] /(idiom) to consider it a pleasure to be among the first to read (or watch or enjoy)/",
            f"先睹為快 先睹为快 [xia{tones[1 - 1]}n du{tones[3 - 1]} we{tones[2 - 1]}i kua{tones[4 - 1]}i] /(idiom) to consider it a pleasure to be among the first to read (or watch or enjoy)/",
        ),
        (
            "千奇百怪 千奇百怪 [qian1 qi2 bai3 guai4] /fantastic oddities of every description (idiom)/",
            f"千奇百怪 千奇百怪 [qia{tones[1 - 1]}n qi{tones[2 - 1]} ba{tones[3 - 1]}i gua{tones[4 - 1]}i] /fantastic oddities of every description (idiom)/",
        ),
        (
            "大熊座 大熊座 [Da4 xiong2 zuo4] /Ursa Major, the Great Bear (constellation)/",
            f"大熊座 大熊座 [Da{tones[4 - 1]} xio{tones[2 - 1]}ng zuo{tones[4 - 1]}] /Ursa Major, the Great Bear (constellation)/",
        ),
        (
            "富得流油 富得流油 [fu4 de5 liu2 you2] /affluent/very rich/",
            f"富得流油 富得流油 [fu{tones[4 - 1]} de{tones[5 - 1]} liu{tones[2 - 1]} yo{tones[2 - 1]}u] /affluent/very rich/",
        ),
        (
            "工學院 工学院 [gong1 xue2 yuan4] /school of engineering/college of engineering/",
            f"工學院 工学院 [go{tones[1 - 1]}ng xue{tones[2 - 1]} yua{tones[4 - 1]}n] /school of engineering/college of engineering/",
        ),
        (
            "奇詭 奇诡 [qi2 gui3] /strange; queer; intriguing/",
            f"奇詭 奇诡 [qi{tones[2 - 1]} gui{tones[3 - 1]}] /strange; queer; intriguing/",
        ),
    ]
    for question, answer in pairs:
        assert tone_numbers_to_marks(question) == answer
