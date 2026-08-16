from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "dbs-publish" / "SKILL.md"
QUESTION = "你准备让小红书把长文直接转成图片，还是使用自己的配图、把长文保留在笔记正文里？"

MODE_A = """图片内标题

```text
别再围观别人的生活
```

图片内长文

```text
注意力不是免费的。
每段只按一次回车。
```

笔记标题

```text
把注意力还给自己
```

正文小结

```text
少一点比较，多一点行动。
```

话题

```text
#注意力 #自我成长
```"""

MODE_B = """标题

```text
把注意力还给自己
```

正文

```text
别人的生活可以看看。
自己的生活更值得认真在场。
```

话题

```text
#注意力 #自我成长
```"""


def fields(text: str):
    matches = re.findall(r"(?m)^([^#\n][^\n]*)\n\n```text\n(.*?)\n```$", text, re.S)
    return [(label.strip(), value) for label, value in matches]


class XiaohongshuLongformContract(unittest.TestCase):
    def test_ambiguous_first_turn_contract_is_exact(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn(QUESTION, text)
        self.assertIn("最终回复只输出这个问题", text)
        self.assertIn("得到回答前不生成标题、正文或话题", text)

    def test_mode_a_has_exactly_five_copy_ready_fields(self):
        parsed = fields(MODE_A)
        self.assertEqual(
            [label for label, _ in parsed],
            ["图片内标题", "图片内长文", "笔记标题", "正文小结", "话题"],
        )
        self._assert_copy_ready(parsed)

    def test_mode_b_has_exactly_three_copy_ready_fields(self):
        parsed = fields(MODE_B)
        self.assertEqual([label for label, _ in parsed], ["标题", "正文", "话题"])
        self._assert_copy_ready(parsed)

    def test_modes_are_mutually_exclusive_in_skill_contract(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("自有配图模式不额外生成第二标题和正文小结", text)
        self.assertIn("长文转图片模式输出", text)
        self.assertIn("通用文章和其他不需要双层文字载体的内容", text)

    def test_skill_contains_single_enter_copy_contract(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("只要发布形态没有被明确说明，就停止成稿流程", text)
        self.assertIn("不得出现连续空行", text)
        self.assertIn("复制即发布", text)
        self.assertIn("每段只按一次回车，不额外插入空白行", text)

    def _assert_copy_ready(self, parsed):
        for label, value in parsed:
            self.assertEqual(value, value.strip(), label)
            self.assertNotIn("\n\n", value, label)
            self.assertNotRegex(value, r"(?m)^(?:#{1,6}\s|[-*+]\s|---+$)", label)
            self.assertNotRegex(value, r"(?m)\s+$", label)


if __name__ == "__main__":
    unittest.main()
