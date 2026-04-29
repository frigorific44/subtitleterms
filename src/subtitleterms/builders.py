from aqt.addons import AddonManager

from .deckbuilder.base import BaseDeck
from .deckbuilder.zh_builder import ZH_Deck, zh_initialize
from .i18n import localization

logger = AddonManager.get_logger("subtitleterms")


builder_tuples: list[tuple[str, BaseDeck]] = [
    (
        f"{localization['zh-Hans']} > {localization['en']}",
        ZH_Deck("zh-Hans", "en", lambda: zh_initialize("simplified")),
    ),
    (
        f"{localization['zh-Hant']} > {localization['en']}",
        ZH_Deck("zh-Hant", "en", lambda: zh_initialize("traditional")),
    ),
]
builders: dict[str, BaseDeck] = {
    dt[0]: dt[1] for dt in sorted(builder_tuples, key=lambda deck: deck[0])
}
