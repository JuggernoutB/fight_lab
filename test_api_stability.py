#!/usr/bin/env python3
# test_api_stability.py - Test API contract stability

"""
Test suite demonstrating API stability features:
1. API versioning for frontend compatibility
2. Input validation for robustness
3. Error handling for production use
"""

from game import run_fight

def test_api_versioning():
    """Test that API includes version information"""
    print("🔖 TESTING API VERSIONING")
    print("-" * 40)

    result = run_fight(
        {"type": "balanced", "role": "BRUISER"},
        {"type": "balanced", "role": "ASSASSIN"},
        {"seed": 42, "include_detailed_log": False}
    )

    # Verify version fields exist
    required_version_fields = ["api_version", "core_version", "event_schema_version"]

    for field in required_version_fields:
        assert field in result, f"Missing version field: {field}"
        print(f"✅ {field}: {result[field]}")

    # Verify version format
    assert result["api_version"] == "1.0"
    assert result["event_schema_version"] == "v1"
    assert result["core_version"].startswith("15.")

    print("✅ All version fields present and correct")


def test_input_validation():
    """Test input validation catches common errors"""
    print("\n🛡️ TESTING INPUT VALIDATION")
    print("-" * 40)

    validation_tests = [
        {
            "name": "Invalid role",
            "config_a": {"type": "balanced", "role": "WIZARD"},
            "config_b": {"type": "balanced", "role": "ASSASSIN"},
            "expected_error": "Invalid role"
        },
        {
            "name": "Stats out of range (too high)",
            "config_a": {"type": "custom", "role": "BRUISER", "stats": {"hp": 25, "attack": 12, "defense": 12, "agility": 12}},
            "config_b": {"type": "balanced", "role": "ASSASSIN"},
            "expected_error": "Invalid hp: 25"
        },
        {
            "name": "Stats out of range (too low)",
            "config_a": {"type": "custom", "role": "BRUISER", "stats": {"hp": 5, "attack": 12, "defense": 12, "agility": 12}},
            "config_b": {"type": "balanced", "role": "ASSASSIN"},
            "expected_error": "Invalid hp: 5"
        },
        {
            "name": "Missing required stat",
            "config_a": {"type": "custom", "role": "BRUISER", "stats": {"hp": 15, "attack": 12}},  # Missing defense, agility
            "config_b": {"type": "balanced", "role": "ASSASSIN"},
            "expected_error": "Missing required stat"
        },
        {
            "name": "Non-integer stat",
            "config_a": {"type": "custom", "role": "BRUISER", "stats": {"hp": 15.5, "attack": 12, "defense": 12, "agility": 12}},
            "config_b": {"type": "balanced", "role": "ASSASSIN"},
            "expected_error": "Invalid hp"
        },
        {
            "name": "Non-dict config",
            "config_a": "invalid_config",
            "config_b": {"type": "balanced", "role": "ASSASSIN"},
            "expected_error": "Fighter config must be a dictionary"
        }
    ]

    for test in validation_tests:
        print(f"\nTesting: {test['name']}")
        try:
            run_fight(test["config_a"], test["config_b"])
            print(f"❌ Should have caught: {test['expected_error']}")
            assert False, f"Validation failed for: {test['name']}"
        except ValueError as e:
            error_msg = str(e)
            if test["expected_error"] in error_msg:
                print(f"✅ Correctly caught: {error_msg}")
            else:
                print(f"❌ Wrong error message. Expected '{test['expected_error']}', got '{error_msg}'")
                assert False, f"Wrong error message for: {test['name']}"
        except Exception as e:
            print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
            assert False, f"Unexpected error for: {test['name']}"

    print("\n✅ All validation tests passed!")


def test_api_contract():
    """Test that API response has expected structure"""
    print("\n📋 TESTING API CONTRACT")
    print("-" * 40)

    # Test with detailed log
    result = run_fight(
        {"type": "balanced", "role": "BRUISER"},
        {"type": "balanced", "role": "ASSASSIN"},
        {"seed": 123, "include_detailed_log": True}
    )

    # Check required top-level fields
    required_fields = [
        "api_version", "core_version", "event_schema_version",
        "winner", "rounds", "fighter_a", "fighter_b", "log", "summary"
    ]

    for field in required_fields:
        assert field in result, f"Missing required field: {field}"

    # Check fighter structure
    for fighter_key in ["fighter_a", "fighter_b"]:
        fighter = result[fighter_key]
        required_fighter_fields = ["role", "final_hp", "final_stamina"]
        for field in required_fighter_fields:
            assert field in fighter, f"Missing fighter field {field} in {fighter_key}"

    # Check summary structure
    summary = result["summary"]
    required_summary_fields = ["total_damage_to_a", "total_damage_to_b", "fight_length"]
    for field in required_summary_fields:
        assert field in summary, f"Missing summary field: {field}"

    # Check log structure (if present)
    if result["log"]:
        event = result["log"][0]
        assert "round" in event, "Missing 'round' in event"
        assert "attacks" in event, "Missing 'attacks' in event"

        if event["attacks"]:
            attack = event["attacks"][0]
            required_attack_fields = ["attacker", "defender", "zone", "damage", "event"]
            for field in required_attack_fields:
                assert field in attack, f"Missing attack field: {field}"

    print("✅ API contract verified - all required fields present")

    # Test without log
    result_no_log = run_fight(
        {"type": "balanced", "role": "TANK"},
        {"type": "balanced", "role": "SKIRMISHER"},
        {"seed": 456, "include_detailed_log": False}
    )

    assert result_no_log["log"] is None, "Log should be None when include_detailed_log=False"
    print("✅ Log exclusion working correctly")


def test_determinism():
    """Test that same seed produces same results"""
    print("\n🎲 TESTING DETERMINISM")
    print("-" * 40)

    seed = 999
    config_a = {"type": "balanced", "role": "BRUISER"}
    config_b = {"type": "balanced", "role": "ASSASSIN"}
    options = {"seed": seed, "include_detailed_log": False}

    # Run same fight twice
    result1 = run_fight(config_a, config_b, options)
    result2 = run_fight(config_a, config_b, options)

    # Compare key results
    assert result1["winner"] == result2["winner"], "Winner should be deterministic"
    assert result1["rounds"] == result2["rounds"], "Rounds should be deterministic"
    assert abs(result1["summary"]["total_damage_to_a"] - result2["summary"]["total_damage_to_a"]) < 0.001, "Damage should be deterministic"

    print(f"✅ Deterministic results: {result1['winner']} wins in {result1['rounds']} rounds")


if __name__ == "__main__":
    print("🧪 API STABILITY TEST SUITE")
    print("=" * 50)

    test_api_versioning()
    test_input_validation()
    test_api_contract()
    test_determinism()

    print("\n🎉 ALL TESTS PASSED!")
    print("\n📱 API is ready for production use:")
    print("  ✅ Versioned responses for frontend compatibility")
    print("  ✅ Input validation prevents crashes")
    print("  ✅ Stable contract guarantees")
    print("  ✅ Deterministic behavior for testing")