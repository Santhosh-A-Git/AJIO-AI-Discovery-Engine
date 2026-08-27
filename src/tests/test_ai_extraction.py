import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.analyzer import analyze_batch

load_dotenv()

# The Golden Test Suite: 15-20 cases of diverse wishlist-to-purchase scenarios
GOLDEN_CASES = [
    {
        "id": "tc1",
        "text": "I added the Levi's jeans to my wishlist a week ago waiting for a price drop. Today they went on a 40% discount but my size 32 is out of stock! So frustrating, I just ended up buying them on Myntra instead.",
        "source": "App Store",
        "expected": {
            "relevance_status": "RELEVANT",
            "wishlist_intent": "PRICE_TRACKING",
            "conversion_blocker": "AVAILABILITY",
            "purchase_status": "BOUGHT_ELSEWHERE"
        }
    },
    {
        "id": "tc2",
        "text": "Saved 5 different kurtas to compare for Diwali. The problem is none of them have customer review photos so I can't tell if the embroidery looks cheap in real life. I'll probably just buy from a local store.",
        "source": "Google Play",
        "expected": {
            "relevance_status": "RELEVANT",
            "wishlist_intent": "COMPARISON",
            "conversion_blocker": "TRUST",
            "purchase_status": "ABANDONED"
        }
    },
    {
        "id": "tc3",
        "text": "The app is so slow, it takes 10 seconds to load the homepage.",
        "source": "Twitter",
        "expected": {
            "relevance_status": "NOT_RELEVANT"
        }
    },
    {
        "id": "tc4",
        "text": "I really want these Puma sneakers for my birthday next month. Just bookmarking them for now so I remember to ask my parents.",
        "source": "Reddit",
        "expected": {
            "relevance_status": "RELEVANT",
            "wishlist_intent": "BOOKMARKING",
            "conversion_blocker": "BUDGET_TIMING",
            "purchase_status": "DELAYED"
        }
    },
    {
        "id": "tc5",
        "text": "Put a dress in my cart but shipping said it would take 8 days? I need it for a party this weekend. Had to cancel and order on Amazon Prime.",
        "source": "App Store",
        "expected": {
            "relevance_status": "RELEVANT",
            "conversion_blocker": "DELIVERY",
            "purchase_status": "BOUGHT_ELSEWHERE"
        }
    },
    {
        "id": "tc6",
        "text": "I love the new winter collection, looks great on the models.",
        "source": "Instagram",
        "expected": {
            "relevance_status": "NOT_RELEVANT" # General praise, no friction
        }
    },
    {
        "id": "tc7",
        "text": "Why is there a limit of 100 items on the wishlist?! I use it as a moodboard for wedding planning and it keeps deleting my old saves. I'm moving to Pinterest.",
        "source": "Play Store",
        "expected": {
            "relevance_status": "RELEVANT",
            "wishlist_intent": "BOOKMARKING",
            "conversion_blocker": "APP_FRICTION",
            "purchase_status": "UNKNOWN"
        }
    },
    {
        "id": "tc8",
        "text": "Added the GAP hoodie but the size chart is so confusing. Does 'L' mean UK 12 or UK 14? Can't risk having to pay for return shipping if it doesn't fit.",
        "source": "Twitter",
        "expected": {
            "relevance_status": "RELEVANT",
            "conversion_blocker": "FIT_SIZE",
            "purchase_status": "ABANDONED"
        }
    },
    {
        "id": "tc9",
        "text": "Found a cool jacket via an Instagram ad. Saved it. Then saw the exact same jacket on Nykaa Fashion for ₹500 cheaper. Obviously bought it there.",
        "source": "Reddit",
        "expected": {
            "relevance_status": "RELEVANT",
            "wishlist_intent": "PRICE_TRACKING",
            "conversion_blocker": "PRICE_VALUE",
            "purchase_status": "BOUGHT_ELSEWHERE"
        }
    },
    {
        "id": "tc10",
        "text": "Is this original? I saved the Nike Air Max but the seller name is 'CloudTail_Fashion_123'. Seems sketchy, don't want to get scammed.",
        "source": "App Store",
        "expected": {
            "relevance_status": "RELEVANT",
            "conversion_blocker": "TRUST",
            "purchase_status": "ABANDONED"
        }
    },
    {
        "id": "tc11",
        "text": "Hi AJIO support, my refund of ₹2400 has not been credited to my bank account since 12 days. Please help.",
        "source": "Twitter",
        "expected": {
            "relevance_status": "NOT_RELEVANT" # Customer support issue, not product discovery friction
        }
    },
    {
        "id": "tc12",
        "text": "Wishlisting items for my baby shower. Hoping my friends buy them from the registry.",
        "source": "Facebook",
        "expected": {
            "relevance_status": "RELEVANT",
            "wishlist_intent": "GIFTING",
            "conversion_blocker": "BUDGET_TIMING",
            "purchase_status": "DELAYED"
        }
    },
    {
        "id": "tc13",
        "text": "The return policy changed to 7 days instead of 30?! I'm not buying these boots until I'm 100% sure, deleting from cart.",
        "source": "Play Store",
        "expected": {
            "relevance_status": "RELEVANT",
            "conversion_blocker": "RETURNS_EXCHANGE",
            "purchase_status": "ABANDONED"
        }
    },
    {
        "id": "tc14",
        "text": "I have 50 items in my cart and can't figure out which to buy. Too many options, getting a headache. I'll do this tomorrow.",
        "source": "Reddit",
        "expected": {
            "relevance_status": "RELEVANT",
            "wishlist_intent": "COMPARISON",
            "conversion_blocker": "DECISION_OVERLOAD",
            "purchase_status": "DELAYED"
        }
    },
    {
        "id": "tc15",
        "text": "Loved the H&M t-shirt but it says 'Dry Clean Only'. For a ₹400 tee? No thanks.",
        "source": "Instagram",
        "expected": {
            "relevance_status": "RELEVANT",
            "conversion_blocker": "QUALITY",
            "purchase_status": "ABANDONED"
        }
    }
]

def test_ai_extraction_constraints():
    """
    Assertion-based structured validation test suite.
    Instead of byte-for-byte JSON equality, we verify that the AI pipeline
    consistently satisfies the defined classification and evidence constraints.
    """
    # Only run if API key is present
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not found. Skipping live API tests.")
        
    for case in GOLDEN_CASES:
        print(f"\\nTesting Case {case['id']}: {case['text'][:50]}...")
        
        # Format for batch
        batch = [{
            "id": case['id'],
            "source": case['source'],
            "text": case['text'],
            "timestamp": "2024-01-01",
            "url": "http://test.com"
        }]
        
        # Run through the pipeline
        results = analyze_batch(batch)
        
        assert len(results) == 1, f"Pipeline dropped record for {case['id']}"
        result = results[0]
        expected = case['expected']
        
        # 1. Test Relevance Status
        assert result['relevance_status'] == expected['relevance_status'], \
            f"Relevance Mismatch: expected {expected['relevance_status']}, got {result['relevance_status']}"
            
        if expected['relevance_status'] == "NOT_RELEVANT":
            # If not relevant, core analytical fields shouldn't be extracted aggressively
            assert result.get('conversion_blocker') in [None, "UNKNOWN", ""], "Should not extract blocker for NOT_RELEVANT"
            continue
            
        # 2. Test core categorical assertions (if explicitly defined in expected)
        for key in ["wishlist_intent", "conversion_blocker", "purchase_status"]:
            if key in expected:
                assert result.get(key) == expected[key], \
                    f"Categorical Mismatch on {key}: expected {expected[key]}, got {result.get(key)}"
                    
        # 3. Test Field-Level Support Validations
        # The AI should mark these fields as 'supported' or 'unsupported' based on evidence
        assert result.get('conversion_blocker_support') in ['supported', 'unsupported', 'unknown'], \
            f"Invalid support status for conversion_blocker: {result.get('conversion_blocker_support')}"
            
        # 4. Semantic Validation for free-text (just ensuring it's populated and not hallucinating)
        assert len(result.get('observed_problem_summary', '')) > 5, "Observed problem summary too short or empty"
        assert len(result.get('theme', '')) >= 3, "Theme must be populated"

if __name__ == "__main__":
    test_ai_extraction_constraints()
