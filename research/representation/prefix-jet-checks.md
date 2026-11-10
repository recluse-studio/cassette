# Reproducible finite check of exact prefix packets

This check executes the identities in [prefix-jet-packets.md](prefix-jet-packets.md).
It uses synthetic exact source families, Python integers, and bitwise XOR. It does not
measure an external drive or a model. The proof obligations are source inversion, direct
packet extraction, exact record recovery, and the address rule for in-place branch choice.
It also changes one source record and checks that a low-degree certificate rejects it.

The seed is 20260920. Every degree from 1 through r is checked for r from 1 through 7.
Each coefficient has three 16-bit words. Every prefix and every completion is checked;
randomness selects coefficient values, not the tested prefix or completion set.

Run the Python block with a standard Python 3 interpreter. Its dictionaries and lists are
an experiment harness, not evidence of the proposed interpreter's RAM usage. The packet's
payload slot count is checked explicitly; integer-address workspace is covered by the proof.

```python
from math import comb
from random import Random
from functools import reduce
from operator import xor

seed = 20260920
generator = Random(seed)
words = 3
word_bits = 16
counts = dict(sources=0, prefixes=0, record_decodes=0,
              prepared_branches=0, rejected_mutations=0)

def xor_arrays(arrays):
    values = list(arrays)
    return tuple(reduce(xor, (v[j] for v in values), 0) for j in range(words))

def reverse_bits(value, width):
    return sum(((value >> j) & 1) << (width - 1 - j) for j in range(width))

def kappa(width, degree):
    return sum(comb(width, j) for j in range(min(width, degree) + 1))

def coefficients_from_values(values, width):
    result = list(values)
    for j in range(width):
        for mask in range(1 << width):
            if mask & (1 << j):
                result[mask] = xor_arrays((result[mask], result[mask ^ (1 << j)]))
    return result

def slot(tail_mask, prefix_ones, degree):
    room = degree - tail_mask.bit_count()
    tag = 0
    for j in range(prefix_ones.bit_length() - 1, -1, -1):
        if room and prefix_ones & (1 << j):
            tag |= 1 << j
            room -= 1
    return tail_mask | tag

for r in range(1, 8):
    n = 1 << r
    for degree in range(1, r + 1):
        support = [s for s in range(n) if s.bit_count() <= degree]
        coefficient = {s: tuple(generator.getrandbits(word_bits) for _ in range(words))
                       for s in support}
        values = [xor_arrays(coefficient[s] for s in support if s & u == s)
                  for u in range(n)]
        recovered = coefficients_from_values(values, r)
        assert all(recovered[s] == coefficient.get(s, (0,) * words) for s in range(n))
        source = [values[reverse_bits(i, r)] for i in range(n)]
        highest = sorted((s for s in support if s.bit_count() == degree),
                         key=lambda s: ((s & -s).bit_length(), s))
        bank = [coefficient[s] for s in highest]
        lower = []
        level_base = []
        restricted = {}
        for h in range(r + 1):
            level_base.append(len(lower))
            t = r - h
            tail_support = [s for s in range(1 << t) if s.bit_count() <= degree]
            lower_support = [s for s in tail_support if 0 < s.bit_count() < degree]
            for p in range(1 << h):
                prefix_ones = reverse_bits(p, h)
                prefix_mask = (1 << h) - 1
                local = {tail: xor_arrays(coefficient[s] for s in support
                                         if s >> h == tail and
                                         (s & prefix_mask) & ~prefix_ones == 0)
                         for tail in tail_support}
                restricted[h, p] = local
                lower.extend(local[s] for s in lower_support)
        expected_arrays = n + len(lower) + len(bank)
        assert expected_arrays <= (2 * degree - 1) * n + comb(r, degree)
        if degree == 1:
            assert expected_arrays == n + r
        if degree == 2:
            assert expected_arrays == 3 * n - r - 2 + comb(r, 2)
        for (h, p), local in restricted.items():
            t = r - h
            tail_support = sorted(local)
            lower_support = [s for s in tail_support if 0 < s.bit_count() < degree]
            fetched = {0: source[p << t]}
            start = level_base[h] + p * len(lower_support)
            fetched.update(zip(lower_support, lower[start:start + len(lower_support)]))
            suffix_count = comb(t, degree) if t >= degree else 0
            start = len(bank) - suffix_count
            assert all(s >> h << h == s for s in highest[start:])
            fetched.update((s >> h, value) for s, value in zip(highest[start:], bank[start:]))
            assert fetched == local
            assert len(fetched) == kappa(t, degree)
            counts['prefixes'] += 1
            for u in range(1 << t):
                target = source[(p << t) | reverse_bits(u, t)]
                assert xor_arrays(fetched[s] for s in fetched if s & u == s) == target
                payload = dict(fetched)
                prefix_ones = 0
                for j in range(t):
                    remaining = [s for s in tail_support if s & ((1 << j) - 1) == 0]
                    addresses = [slot(s, prefix_ones, degree) for s in remaining]
                    assert len(set(addresses)) == len(remaining)
                    for a in remaining:
                        if a & (1 << j) or a.bit_count() >= degree:
                            continue
                        left = slot(a, prefix_ones, degree)
                        right = slot(a | (1 << j), prefix_ones, degree)
                        payload[right] = xor_arrays((payload[left], payload[right]))
                        counts['prepared_branches'] += 1
                    if u & (1 << j):
                        prefix_ones |= 1 << j
                    selected = {s: payload[slot(s, prefix_ones, degree)]
                                for s in tail_support if s & ((1 << (j + 1)) - 1) == 0}
                    direct = {s: xor_arrays(fetched[q] for q in tail_support
                                            if q >> (j + 1) == s >> (j + 1) and
                                            q & ((1 << (j + 1)) - 1) & ~prefix_ones == 0)
                              for s in selected}
                    assert selected == direct
                    assert len(payload) == kappa(t, degree)
                assert payload[slot(0, prefix_ones, degree)] == target
                counts['record_decodes'] += 1
        if degree < r:
            changed = list(values)
            changed[0] = (changed[0][0] ^ 1, *changed[0][1:])
            changed_coefficients = coefficients_from_values(changed, r)
            assert any(any(changed_coefficients[s]) for s in range(n)
                       if s.bit_count() > degree)
            counts['rejected_mutations'] += 1
        counts['sources'] += 1

print(dict(seed=seed, **counts))
```

The block completed successfully on 2026-09-20 and printed:

```text
{'seed': 20260920, 'sources': 28, 'prefixes': 3048, 'record_decodes': 11260, 'prepared_branches': 196070, 'rejected_mutations': 21}
```

Passing a finite check supports the symbolic proof; it does not turn the structured synthetic
family into a model benchmark.
