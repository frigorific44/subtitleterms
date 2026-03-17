from aqt.addons import AddonManager

from .deckbuilder.base import BaseDeck
from .deckbuilder.zh_builder import ZH_Deck, zh_initialize

logger = AddonManager.get_logger("subtitleterms")


builder_tuples: list[tuple[str, BaseDeck]] = [
    (
        "Chinese (Simplified) > English",
        ZH_Deck("ZH_SC", "EN", lambda x: zh_initialize(x, "simplified")),
    ),
    (
        "Chinese (Traditional) > English",
        ZH_Deck("ZH_TC", "EN", lambda x: zh_initialize(x, "traditional")),
    ),
]
builders: dict[str, BaseDeck] = {
    dt[0]: dt[1] for dt in sorted(builder_tuples, key=lambda deck: deck[0])
}
