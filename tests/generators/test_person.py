#!/usr/bin/env python3
"""
Tests for earth.generators.person module.
Tests person generation, validation, and data quality.
"""

import sys
from pathlib import Path
import uuid

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "app"))

try:
    from earth.generators.person import generate_multiple_persons
    from earth.core.utils import PersonProfile
except ImportError as e:
    print(f"❌ Import error in test_person: {e}")
    sys.exit(1)


def test_single_person_generation():
    """Test generating a single person with various parameters."""
    print("🧪 Testing single person generation...")

    try:
        # Generate with seed for reproducibility
        persons = generate_multiple_persons(1, seed=42)

        assert len(persons) == 1, "Should generate exactly 1 person"

        person = persons[0]

        # Test basic attributes
        assert isinstance(person, PersonProfile), "Should be PersonProfile instance"
        assert person.person_id is not None, "Should have person ID"
        assert person.full_name is not None, "Should have name"
        assert person.age >= 18, "Should be adult (18+)"
        assert person.age <= 85, "Should be reasonable age (<=85)"
        assert person.job_title is not None, "Should have job title"
        assert person.annual_income > 0, "Should have positive income"
        assert person.email is not None, "Should have email"
        assert "@" in person.email, "Email should be valid format"
        assert person.city is not None, "Should have city"
        assert person.state is not None, "Should have state"

        print(f"  Generated: {person.full_name}, {person.age} years old")
        print(f"  Job: {person.job_title}, Income: ${person.annual_income:,}")

        print("✅ Single person generation tests passed")
        return True

    except Exception as e:
        print(f"❌ Single person generation test failed: {e}")
        return False


def test_multiple_person_generation():
    """Test generating multiple persons."""
    print("🧪 Testing multiple person generation...")

    try:
        count = 10
        persons = generate_multiple_persons(count, seed=123)

        assert len(persons) == count, f"Should generate exactly {count} persons"

        # Test uniqueness
        person_ids = [p.person_id for p in persons]
        assert len(set(person_ids)) == count, "All person IDs should be unique"

        names = [p.full_name for p in persons]
        # Names might not be unique, but should have variety
        unique_names = len(set(names))
        assert unique_names >= count * 0.8, "Should have good name variety"

        # Test age distribution
        ages = [p.age for p in persons]
        assert min(ages) >= 18, "All should be adults"
        assert max(ages) <= 85, "All should be reasonable age"
        assert len(set(ages)) >= 5, "Should have age variety"

        # Test income distribution
        incomes = [p.annual_income for p in persons]
        assert all(income > 0 for income in incomes), "All should have positive income"
        assert max(incomes) > min(incomes), "Should have income variety"

        print(f"  Generated {count} persons")
        print(f"  Age range: {min(ages)} - {max(ages)}")
        print(f"  Income range: ${min(incomes):,} - ${max(incomes):,}")
        print(f"  Unique names: {unique_names}/{count}")

        print("✅ Multiple person generation tests passed")
        return True

    except Exception as e:
        print(f"❌ Multiple person generation test failed: {e}")
        return False


def test_data_quality():
    """Test data quality and constraints."""
    print("🧪 Testing data quality...")

    try:
        # Generate a larger sample for quality testing
        persons = generate_multiple_persons(50, seed=555)

        # Test age constraints
        ages = [p.age for p in persons]
        assert all(18 <= age <= 85 for age in ages), "Ages should be in valid range"

        # Test income constraints
        incomes = [p.annual_income for p in persons]
        assert all(income > 0 for income in incomes), "Incomes should be positive"
        assert all(
            income <= 1000000 for income in incomes
        ), "Incomes should be reasonable"

        # Test email format
        emails = [p.email for p in persons]
        for email in emails:
            assert "@" in email, f"Email should contain @: {email}"
            assert (
                "." in email.split("@")[1]
            ), f"Email should have valid domain: {email}"

        # Test name quality
        names = [p.full_name for p in persons]
        for name in names:
            assert len(name) > 2, f"Name should be reasonable length: {name}"
            assert " " in name, f"Name should have first and last name: {name}"

        # Test job title quality
        job_titles = [p.job_title for p in persons]
        for title in job_titles:
            assert len(title) > 2, f"Job title should be reasonable: {title}"

        # Test location quality
        cities = [p.city for p in persons]
        states = [p.state for p in persons]

        for city in cities:
            assert len(city) > 1, f"City should be reasonable: {city}"

        for state in states:
            assert len(state) == 2, f"State should be 2-letter code: {state}"
            assert state.isupper(), f"State should be uppercase: {state}"

        # Test diversity
        unique_ages = len(set(ages))
        unique_jobs = len(set(job_titles))
        unique_cities = len(set(cities))
        unique_states = len(set(states))

        assert unique_ages >= 10, f"Should have age diversity: {unique_ages}"
        assert unique_jobs >= 10, f"Should have job diversity: {unique_jobs}"
        assert unique_cities >= 5, f"Should have city diversity: {unique_cities}"
        assert unique_states >= 3, f"Should have state diversity: {unique_states}"

        print(f"  Tested 50 persons for data quality")
        print(f"  Age range: {min(ages)} - {max(ages)} ({unique_ages} unique)")
        print(f"  Income range: ${min(incomes):,} - ${max(incomes):,}")
        print(f"  Job diversity: {unique_jobs} unique titles")
        print(f"  Location diversity: {unique_cities} cities, {unique_states} states")

        print("✅ Data quality tests passed")
        return True

    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("🧪 Testing edge cases...")

    try:
        # Test generating zero persons
        persons_zero = generate_multiple_persons(0, seed=111)
        assert len(persons_zero) == 0, "Should generate zero persons"

        # Test generating one person
        persons_one = generate_multiple_persons(1, seed=222)
        assert len(persons_one) == 1, "Should generate one person"

        # Test large batch generation
        large_count = 1000
        persons_large = generate_multiple_persons(large_count, seed=333)
        assert (
            len(persons_large) == large_count
        ), f"Should generate {large_count} persons"

        # Test that large generation maintains quality
        ages = [p.age for p in persons_large]
        assert all(
            18 <= age <= 85 for age in ages
        ), "Large generation should maintain age constraints"

        print(f"  Tested zero, one, and {large_count} person generation")
        print(f"  Tested edge cases in batch generation")

        print("✅ Edge cases tests passed")
        return True

    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        return False


def display_sample_data():
    """Display sample generated data."""
    print("\n👥 Sample Person Data:")
    print("-" * 60)

    try:
        persons = generate_multiple_persons(3, seed=12345)

        for i, person in enumerate(persons, 1):
            print(f"\n{i}. {person.full_name} ({person.age} years old)")
            print(f"   ID: {person.person_id}")
            print(f"   Job: {person.job_title}")
            print(f"   Income: ${person.annual_income:,}/year")
            print(f"   Email: {person.email}")
            print(f"   Location: {person.city}, {person.state}")

    except Exception as e:
        print(f"❌ Error displaying sample data: {e}")


def main():
    """Run all person generator tests."""
    print("👥 Person Generator Tests")
    print("=" * 50)

    tests = [
        test_single_person_generation,
        test_multiple_person_generation,
        test_data_quality,
        test_edge_cases,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1

    # Display sample data
    display_sample_data()

    print(f"\n📊 Person Generator Tests - Passed: {passed}, Failed: {failed}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
