"""
주요 종목 사전 정의 설정

한국 주요 대형주들의 경제적 해자와 경영진 평가를 미리 정의합니다.
"""

from typing import Dict, Optional


# 주요 종목의 사전 정의 설정
STOCK_PRESETS: Dict[str, Dict] = {
    # 삼성전자
    "005930": {
        "moat": {
            "has_brand_power": True,        # 삼성 브랜드 파워
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 반도체 대규모 생산
            "has_intangible_assets": True    # 특허, 기술력
        },
        "mgmt": {
            "transparency_score": 4,         # 투명성 양호
            "shareholder_return_score": 4,   # 배당 꾸준
            "capital_allocation_score": 5,   # 반도체 투자 우수
            "governance_score": 3            # 지배구조 보통
        }
    },

    # SK하이닉스
    "000660": {
        "moat": {
            "has_brand_power": False,
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 메모리 반도체 생산
            "has_intangible_assets": True    # 기술력
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 3
        }
    },

    # 카카오
    "035720": {
        "moat": {
            "has_brand_power": True,         # 카카오톡 브랜드
            "has_switching_cost": True,      # 메신저 전환 비용
            "has_network_effect": True,      # 네트워크 효과 강력
            "has_cost_advantage": False,
            "has_intangible_assets": False
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 4
        }
    },

    # NAVER
    "035420": {
        "moat": {
            "has_brand_power": True,         # 네이버 브랜드
            "has_switching_cost": True,      # 검색, 쇼핑 전환 비용
            "has_network_effect": True,      # 플랫폼 네트워크 효과
            "has_cost_advantage": False,
            "has_intangible_assets": False
        },
        "mgmt": {
            "transparency_score": 5,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 4
        }
    },

    # LG화학
    "051910": {
        "moat": {
            "has_brand_power": False,
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 배터리 생산 규모
            "has_intangible_assets": True    # 배터리 기술
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 3
        }
    },

    # 삼성SDI
    "006400": {
        "moat": {
            "has_brand_power": False,
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 배터리 생산
            "has_intangible_assets": True    # 배터리 기술
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 3
        }
    },

    # 삼성바이오로직스
    "207940": {
        "moat": {
            "has_brand_power": False,
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 바이오 생산 규모
            "has_intangible_assets": True    # 바이오 기술
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 3
        }
    },

    # 셀트리온
    "068270": {
        "moat": {
            "has_brand_power": False,
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 바이오시밀러 생산
            "has_intangible_assets": True    # 바이오 기술
        },
        "mgmt": {
            "transparency_score": 3,
            "shareholder_return_score": 2,
            "capital_allocation_score": 4,
            "governance_score": 3
        }
    },

    # 현대차
    "005380": {
        "moat": {
            "has_brand_power": True,         # 현대차 브랜드
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 대규모 생산
            "has_intangible_assets": False
        },
        "mgmt": {
            "transparency_score": 3,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 2
        }
    },

    # 기아
    "000270": {
        "moat": {
            "has_brand_power": True,         # 기아 브랜드
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 대규모 생산
            "has_intangible_assets": False
        },
        "mgmt": {
            "transparency_score": 3,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 2
        }
    },

    # 포스코홀딩스
    "005490": {
        "moat": {
            "has_brand_power": False,
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": True,      # 철강 생산 규모
            "has_intangible_assets": False
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 4,
            "capital_allocation_score": 3,
            "governance_score": 3
        }
    },

    # 삼성물산
    "028260": {
        "moat": {
            "has_brand_power": True,         # 삼성 브랜드
            "has_switching_cost": False,
            "has_network_effect": False,
            "has_cost_advantage": False,
            "has_intangible_assets": False
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 3,
            "capital_allocation_score": 4,
            "governance_score": 3
        }
    },

    # KB금융
    "105560": {
        "moat": {
            "has_brand_power": True,         # KB 브랜드
            "has_switching_cost": True,      # 금융 전환 비용
            "has_network_effect": True,      # 고객 네트워크
            "has_cost_advantage": False,
            "has_intangible_assets": False
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 4,
            "capital_allocation_score": 3,
            "governance_score": 3
        }
    },

    # 신한지주
    "055550": {
        "moat": {
            "has_brand_power": True,         # 신한 브랜드
            "has_switching_cost": True,      # 금융 전환 비용
            "has_network_effect": True,      # 고객 네트워크
            "has_cost_advantage": False,
            "has_intangible_assets": False
        },
        "mgmt": {
            "transparency_score": 4,
            "shareholder_return_score": 4,
            "capital_allocation_score": 3,
            "governance_score": 3
        }
    },
}


# 기본 설정 (사전 정의되지 않은 종목용)
DEFAULT_CONFIG = {
    "moat": {
        "has_brand_power": False,
        "has_switching_cost": False,
        "has_network_effect": False,
        "has_cost_advantage": False,
        "has_intangible_assets": False
    },
    "mgmt": {
        "transparency_score": 3,
        "shareholder_return_score": 3,
        "capital_allocation_score": 3,
        "governance_score": 3
    }
}


def get_stock_config(ticker: str) -> Dict:
    """
    종목 코드에 대한 설정 반환

    Args:
        ticker: 종목 코드 (6자리, 예: "005930")

    Returns:
        해당 종목의 설정 (사전 정의 또는 기본값)
    """
    # 6자리 코드만 추출 (.KS 제거)
    clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')

    return STOCK_PRESETS.get(clean_ticker, DEFAULT_CONFIG)


def is_preset_available(ticker: str) -> bool:
    """
    종목이 사전 정의되어 있는지 확인

    Args:
        ticker: 종목 코드

    Returns:
        사전 정의 여부
    """
    clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')
    return clean_ticker in STOCK_PRESETS


def get_available_presets() -> list:
    """
    사전 정의된 모든 종목 코드 반환

    Returns:
        종목 코드 리스트
    """
    return list(STOCK_PRESETS.keys())
