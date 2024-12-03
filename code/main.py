from KTapeTM import KTapeTM


def test_tm_on_inputs(tm, accept_cases, reject_cases):
    print(f"\nTesting {tm.name}:")
    print("=" * 50)

    print("\nShould Accept:")
    print("-" * 20)
    for input_str in accept_cases:
        print(f"\nTesting input: '{input_str}'")
        print("-" * 30)
        result = tm.run(input_str, save_output=True)
        if not result:
            print(f"ERROR: '{input_str}' was rejected but should accept")

    print("\nShould Reject:")
    print("-" * 20)
    for input_str in reject_cases:
        print(f"\nTesting input: '{input_str}'")
        print("-" * 30)
        result = tm.run(input_str, save_output=True)
        if result:
            print(f"ERROR: '{input_str}' was accepted but should reject")


def main():
    # Test cases for a^i b a^i
    equal_as_accept = ["aba", "aabaa", "aaabaaa"]
    equal_as_reject = ["abaaa", "aa", "b", "ab", ""]

    # Test cases for 0^i 1^i
    equal_01_accept = ["01", "0011", "000111"]
    equal_01_reject = ["0", "1", "00", "11", "011", ""]

    # Test 2-tape equal a's machine
    print("\nTesting 1-tape equal a's machine:")
    tm2 = KTapeTM.from_file("test/equal_as.txt")
    test_tm_on_inputs(tm2, equal_as_accept, equal_as_reject)

    # Test 2-tape equal 0s and 1s machine
    print("\nTesting 2-tape equal 0s and 1s machine:")
    tm3 = KTapeTM.from_file("test/equal0s1s_k2.txt")
    test_tm_on_inputs(tm3, equal_01_accept, equal_01_reject)

    # Test 1-tape equal 0s and 1s machine which k tape machine should be able to do
    print("\nTesting 1-tape equal 0s and 1s machine:")
    tm4 = KTapeTM.from_file("test/equal0s1s_k1.txt")
    test_tm_on_inputs(tm4, equal_01_accept, equal_01_reject)


if __name__ == "__main__":
    main()
