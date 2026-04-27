# Combat System: Damage Calculation Logic

This document formalizes the full damage resolution pipeline, including all combat mechanics and the new **Damage → Resource → Scaling** system.

---

## 1. Attack Initialization

For each attack action:
- Attacker selects 1–2 attack zones
- Defender selects 0–2 defense zones
- Each attack is resolved independently per zone

---

## 2. Base Damage Calculation

Base damage is derived from attacker stats:
- Attack stat defines raw damage output
- Stamina state may apply fatigue modifiers

Result:
→ `base_damage`

---

## 3. Zone Resolution

Check whether the attacked zone is defended:

### 3.1 If zone is defended
- Attempt **block**

### 3.2 If zone is not defended
- Proceed to **dodge check**

---

## 4. Dodge Phase (Unblocked Zones Only)

Dodge is evaluated before damage application:

Possible outcomes:
1. **Full Dodge**
   - Damage = 0
2. **Glancing Hit**
   - Damage reduced (partial hit)
3. **No Dodge**
   - Full damage continues

Result:
→ `post_dodge_damage`

---

## 5. Block Phase (Defended Zones Only)

If zone is defended:

### 5.1 Block Success
- Damage reduced by defense
- Blocked portion is recorded as **absorbed damage**

### 5.2 Block Break
- Occurs if attacker overcomes defense
- Reduced mitigation

Result:
→ `post_block_damage`
→ `absorbed_damage (block only)`

---

## 6. Critical Strike Phase

Critical is evaluated **independently of dodge and block**.

- Can apply to:
  - Full hits
  - Glancing hits
  - Blocked hits

Effect:
- Multiplies final damage

Result:
→ `post_crit_damage`

---

## 7. Final Damage Output

Final damage is applied to HP:

→ `final_damage`

---


## 8. End-of-Round Updates

After all attacks:

1. Apply damage to HP
2. Apply stamina costs
3. Update meta-state

---

## 9. Core Design Principles

### 9.1 Separation of Mechanics
- Damage, dodge, block, crit are independent layers

### 9.2 No Role Hardcoding
- All mechanics depend only on stats
- Roles emerge naturally from stat distribution

---

## 10. Summary Flow

Attack → Zone Check → Dodge/Block → Crit → Damage Applied → Resource Generated → Scaling Applied → Stamina Updated

---

This document defines the **canonical combat pipeline** and should be used as the reference for further balancing and implementation.

