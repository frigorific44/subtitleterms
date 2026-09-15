from subtitleterms.ext import parse_srt


def without_x(ls, *args):
    return [item for i, item in enumerate(ls) if i not in set(args)]


class TestParseSrt:
    def __init__(self):
        self.t_str = [
            "1",
            "00:02:38,166 --> 00:02:39,466",
            "现在？",
            "",
            "2",
            "00:06:48,433 --> 00:06:50,466",
            "人力资源部 人事升迁审查",
            "",
            "3",
            "00:06:50,700 --> 00:06:54,800",
            "10点到11点 广告公司会来提出",
            "明年度饭店的形象提案",
        ]
        self.answer = [
            "现在？",
            "人力资源部 人事升迁审查",
            "10点到11点 广告公司会来提出",
            "明年度饭店的形象提案",
        ]

    def test_parse_srt(self):
        s = "\n".join(self.t_str)
        assert parse_srt(s) == self.answer

    def test_parse_srt_bad_index(self):
        s = "\n".join(without_x(self.t_str, 4))
        assert parse_srt(s) == without_x(self.answer, 1)

    def test_parse_srt_bad_time(self):
        s = "\n".join(without_x(self.t_str, 5, 9))
        assert parse_srt(s) == without_x(self.answer, 1, 2, 3)
