"""
motion_library/catalog.py - Comprehensive Reusable Motion Graphics Catalog.

Standardized, mobile-first motion graphics templates with:
1. High-contrast fine-tuned color system (palette.py).
2. Light glassy background (translucent frosted glassmorphism).
3. Large, bold typography (34pt-36pt headline, punchy pill badges, zero micro-text clutter).
4. Cached vector icons and emotional visual anchors directly embedded on glass plates.
5. Full domain coverage: Academia, Research, Quantum, Math, Tech, AI, Finance, Banking, Instruments, Crypto, Risk, Sentiment.
"""

from .palette import DOMAIN_PRESETS, to_tuple_color

MOTION_CATALOG = {
    # 1. Macroeconomics, Capital Markets & Growth Trends
    "macro_markets": {
        "template": "market_trend",
        "asset_name": "market_trend.mov",
        "icon": "trending-up",
        "title": "CAPITAL MARKETS",
        "badge": "+18.4% ALPHA",
        "badge_color": DOMAIN_PRESETS["finance_markets"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["finance_markets"]["accent_primary"],
        "keywords_en": [
            "financial stability", "macroeconomic", "macro", "capital market", "capital markets",
            "monetary policy", "interest rates", "liquidity", "central bank", "stocks", "growth",
            "bullish", "bearish", "equities"
        ],
        "keywords_darija": ["الاستقرار المالي", "السياسة الاقتصادية", "أسواق المال", "البورصة", "التضخم", "السيولة"]
    },

    # 2. Crypto Ecosystem, Digital Tokens & Unbacked Assets
    "crypto_ecosystem": {
        "template": "crypto_flow",
        "asset_name": "crypto_flow.mov",
        "icon": "blocks",
        "title": "CRYPTO ECOSYSTEM",
        "badge": "UNBACKED ASSETS",
        "badge_color": DOMAIN_PRESETS["crypto_blockchain"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["crypto_blockchain"]["accent_primary"],
        "keywords_en": [
            "crypto", "crypto-assets", "crypto ecosystem", "unbacked", "bitcoin", "ethereum",
            "blockchain", "digital assets", "tokens", "wallet", "web3", "hashrate"
        ],
        "keywords_darija": ["العملات الرقمية", "كريبتو", "بلوكشين", "أصول غير مدعومة", "بيتكوين", "إيثيريوم"]
    },

    # 3. Systemic Risk, Regulation & Contagion Alerts
    "systemic_risk": {
        "template": "risk_meter",
        "asset_name": "risk_meter.mov",
        "icon": "alert-triangle",
        "title": "SYSTEMIC RISK",
        "badge": "82% HIGH EXPOSURE",
        "badge_color": DOMAIN_PRESETS["systemic_risk"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["systemic_risk"]["accent_primary"],
        "keywords_en": [
            "regulatory", "regulation", "vulnerabilities", "systemic", "contagion",
            "challenges", "risk", "financial risk", "stability board", "supervision", "stress test", "exposure"
        ],
        "keywords_darija": ["التنظيم المالي", "المخاطر النظامية", "هشاشة", "تحديات رقابية", "استقرار", "أزمة مالية"]
    },

    # 4. Decentralized Finance (DeFi) & P2P Constellation Mesh
    "defi_architecture": {
        "template": "network_mesh",
        "asset_name": "network_mesh.mov",
        "icon": "network",
        "title": "DECENTRALIZED ARCHITECTURE",
        "badge": "P2P CONSENSUS",
        "badge_color": DOMAIN_PRESETS["ai_technology"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["finance_markets"]["accent_primary"],
        "keywords_en": [
            "disintermediate", "disintermediation", "decentralized", "manner",
            "peer-to-peer", "smart contracts", "protocols", "p2p", "consensus", "defi", "distributed"
        ],
        "keywords_darija": ["إلغاء الوساطة", "التمويل اللامركزي", "عقود ذكية", "بروتوكول", "ند لند"]
    },

    # 5. Banking Institutions & Central Banking Vault
    "banking_institutions": {
        "template": "banking_vault",
        "asset_name": "banking_vault.mov",
        "icon": "landmark",
        "title": "CENTRAL BANKING",
        "badge": "PRUDENTIAL RESERVES",
        "badge_color": DOMAIN_PRESETS["banking_institutions"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["banking_institutions"]["accent_primary"],
        "keywords_en": [
            "bank", "banks", "banking", "central bank", "commercial bank", "reserves",
            "treasury", "liquidity facility", "deposit", "fdic", "basel", "fractional"
        ],
        "keywords_darija": ["البنوك", "البنك المركزي", "احتياطي", "خزينة", "ودائع", "سيولة بنكية"]
    },

    # 6. Financial Instruments, Bonds & Yield Curves
    "financial_instruments": {
        "template": "instruments_spread",
        "asset_name": "instruments_spread.mov",
        "icon": "candlestick-chart",
        "title": "FINANCIAL INSTRUMENTS",
        "badge": "YIELD SPREAD",
        "badge_color": DOMAIN_PRESETS["financial_instruments"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["financial_instruments"]["accent_primary"],
        "keywords_en": [
            "instrument", "instruments", "bonds", "derivatives", "options",
            "swaps", "yield curve", "fixed income", "treasuries", "spread", "coupon", "maturity"
        ],
        "keywords_darija": ["أدوات مالية", "سندات", "مشتقات", "عائد", "فوائد", "خيارات"]
    },

    # 7. Artificial Intelligence & Neural Compute
    "ai_technology": {
        "template": "ai_neural",
        "asset_name": "ai_neural.mov",
        "icon": "brain",
        "title": "ARTIFICIAL INTELLIGENCE",
        "badge": "NEURAL COMPUTE",
        "badge_color": DOMAIN_PRESETS["ai_technology"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["ai_technology"]["accent_primary"],
        "keywords_en": [
            "ai", "artificial intelligence", "neural", "deep learning", "machine learning",
            "model", "transformer", "llm", "tokens", "compute", "algorithm", "inference", "gpu"
        ],
        "keywords_darija": ["الذكاء الاصطناعي", "تعلم الآلة", "شبكات عصبية", "خوارزميات", "نماذج الذكاء"]
    },

    # 8. Quantitative Formulas & Sharpe Ratio Metric
    "quant_calc": {
        "template": "algorithm_metric",
        "asset_name": "algorithm_metric.mov",
        "icon": "calculator",
        "title": "SHARPE RATIO: (Rp - Rf) / σ",
        "badge": "S = 2.45 // ALPHA",
        "badge_color": DOMAIN_PRESETS["finance_markets"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["finance_markets"]["accent_primary"],
        "keywords_en": [
            "calculate", "calculation", "formula", "equation", "sharpe ratio",
            "black scholes", "expected value", "probability", "statistics", "quant", "variance", "alpha"
        ],
        "keywords_darija": ["حساب", "معادلة", "نسبة", "احتمال", "إحصاء", "شارب ريشيو", "رياضيات"]
    },

    # 9. Core Policy Framework & Global Governance
    "policy_thesis": {
        "template": "policy_framework",
        "asset_name": "policy_framework.mov",
        "icon": "scroll",
        "title": "POLICY FRAMEWORK",
        "badge": "GLOBAL STANDARDS",
        "badge_color": DOMAIN_PRESETS["crypto_blockchain"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["finance_markets"]["accent_primary"],
        "keywords_en": [
            "thesis", "core thesis", "scope", "primary scope", "framework",
            "policy", "recommendations", "governance", "standard", "fsb", "oversight"
        ],
        "keywords_darija": ["الأطروحة الأساسية", "نطاق البحث", "إطار تنظيمي", "معايير دولية", "حوكمة"]
    },

    # 10. Academic Thesis, Research & Methodology (NEW)
    "academic_thesis": {
        "template": "academic_thesis",
        "asset_name": "academic_thesis.mov",
        "icon": "graduation-cap",
        "title": "PEER REVIEW THESIS",
        "badge": "EMPIRICAL PROOF",
        "badge_color": DOMAIN_PRESETS["academia_research"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["academia_research"]["accent_primary"],
        "keywords_en": [
            "academic", "academia", "thesis", "dissertation", "peer review", "journal",
            "paper", "methodology", "empirical", "hypothesis", "university", "faculty", "research"
        ],
        "keywords_darija": ["بحث علمي", "أطروحة", "أكاديمي", "دراسة", "منهجية", "جامعة", "فرضية"]
    },

    # 11. Quantum Mechanics & Superposition (NEW)
    "quantum_physics": {
        "template": "quantum_physics",
        "asset_name": "quantum_physics.mov",
        "icon": "atom",
        "title": "QUANTUM MECHANICS",
        "badge": "SUPERPOSITION",
        "badge_color": DOMAIN_PRESETS["quantum_science"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["quantum_science"]["accent_primary"],
        "keywords_en": [
            "quantum", "physics", "superposition", "wave function", "qubit", "entanglement",
            "particle", "orbital", "schrodinger", "coherence", "atomic"
        ],
        "keywords_darija": ["ميكانيكا الكم", "فيزياء", "تراكب كمي", "تشابك كمي", "جسيمات", "ذرة"]
    },

    # 12. Calculus, Proofs & Integrals (NEW)
    "calculus_integral": {
        "template": "calculus_integral",
        "asset_name": "calculus_integral.mov",
        "icon": "sigma",
        "title": "INTEGRAL CALCULUS",
        "badge": "CONVERGENCE",
        "badge_color": DOMAIN_PRESETS["math_statistics"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["math_statistics"]["accent_primary"],
        "keywords_en": [
            "calculus", "integral", "derivative", "differential", "proof", "riemann",
            "convergence", "summation", "sigma", "limit", "theorem", "lemma"
        ],
        "keywords_darija": ["تكامل", "تفاضل", "برهان رياضي", "تقارب", "متتالية", "نظرية رياضية"]
    },

    # 13. Statistical Distribution & Confidence (NEW)
    "data_distribution": {
        "template": "data_distribution",
        "asset_name": "data_distribution.mov",
        "icon": "line-chart",
        "title": "NORMAL DISTRIBUTION",
        "badge": "P < 0.01 CONFIDENCE",
        "badge_color": DOMAIN_PRESETS["math_statistics"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["math_statistics"]["accent_primary"],
        "keywords_en": [
            "distribution", "normal distribution", "gaussian", "bell curve", "standard deviation",
            "confidence interval", "p-value", "significance", "variance", "hypothesis testing"
        ],
        "keywords_darija": ["توزيع طبيعي", "إحصاء", "انحراف معياري", "دلالة إحصائية", "عينات", "بيانات"]
    },

    # 14. Citation Network & Academic Impact (NEW)
    "citation_network": {
        "template": "citation_network",
        "asset_name": "citation_network.mov",
        "icon": "citation",
        "title": "CITATION GRAPH",
        "badge": "IMPACT FACTOR: 28.4",
        "badge_color": DOMAIN_PRESETS["academia_research"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["academia_research"]["accent_primary"],
        "keywords_en": [
            "citation", "citations", "impact factor", "h-index", "bibliography", "referenced",
            "seminal paper", "academic consensus", "literature review", "scholarly"
        ],
        "keywords_darija": ["اقتباسات", "مراجع علمية", "معامل التأثير", "أبحاث سابقة", "مراجعة علمية"]
    },

    # 15. Order Book Depth & Market Liquidity (NEW)
    "order_book": {
        "template": "order_book",
        "asset_name": "order_book.mov",
        "icon": "candlestick-chart",
        "title": "ORDER BOOK DEPTH",
        "badge": "BID/ASK SPREAD",
        "badge_color": DOMAIN_PRESETS["finance_markets"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["finance_markets"]["accent_primary"],
        "keywords_en": [
            "order book", "market depth", "bid ask", "spread", "liquidity depth",
            "slippage", "limit order", "market maker", "hft"
        ],
        "keywords_darija": ["دفتر الأوامر", "عمق السوق", "عروض وطلبات", "سيولة السوق", "فارق السعر"]
    },

    # 16. Market Sentiment & Greed Gauge (NEW)
    "market_sentiment": {
        "template": "sentiment_meter",
        "asset_name": "sentiment_meter.mov",
        "icon": "flame",
        "title": "MARKET SENTIMENT",
        "badge": "GREED: 84 / 100",
        "badge_color": DOMAIN_PRESETS["market_sentiment"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["market_sentiment"]["accent_primary"],
        "keywords_en": [
            "sentiment", "fear and greed", "market sentiment", "fomo", "panic",
            "euphoria", "psychology", "inflow", "conviction"
        ],
        "keywords_darija": ["معنويات السوق", "مؤشر الخوف والطمع", "حماس المستثمرين", "سيكولوجية السوق"]
    },

    # 17. Smart Contract Security Audit (NEW)
    "smart_audit": {
        "template": "smart_audit",
        "asset_name": "smart_audit.mov",
        "icon": "shield-check",
        "title": "SECURITY AUDIT",
        "badge": "ZERO EXPLOITS",
        "badge_color": DOMAIN_PRESETS["crypto_blockchain"]["badge_color"],
        "accent_color": DOMAIN_PRESETS["crypto_blockchain"]["accent_primary"],
        "keywords_en": [
            "audit", "security audit", "smart contract audit", "vulnerability", "exploit",
            "reentrancy", "formal verification", "certik", "openzeppelin"
        ],
        "keywords_darija": ["تدقيق أمني", "فحص العقود الذكية", "ثغرات أمنية", "حماية", "أمان"]
    }
}
