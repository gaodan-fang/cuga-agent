---
description: Guide compliance agent to apply role-based travel policies when analyzing
  options
enabled: true
id: tool_guide_compliance_policy_guide
name: Travel Policy Compliance Guide
prepend: true
priority: 90
target_tools:
- analyze_travel_compliance
triggers:
  always: true
type: tool_guide
---

# Role-Based Travel Policy Enforcement

When filtering or validating travel options, you must strictly apply role-based company policies. Use the policy information from the YAML files in `travel_agent/config/policies/` directory.

## Policy Limits by Role

### Employee Policy
**Flight Constraints:**
- Maximum cost per person: **$500**
- Allowed classes: **economy only**
- Maximum layovers: 2
- Direct flight preference: not required

**Hotel Constraints:**
- Maximum rate per night: **$150**
- Minimum rating: 3.0 stars
- Allowed classes: standard, comfort
- Required amenities: Free Wi-Fi

**Budget Constraints:**
- Maximum total budget: **$2,000**
- Meal per diem: $50/day
- Ground transport: $50/day
- Incidentals: $25/day

**Approval Requirements:**
- Approval required: Yes
- Approver role: approving_manager
- Auto-approve threshold: Under $1,000

---

### Manager Policy
**Flight Constraints:**
- Maximum cost per person: **$800**
- Allowed classes: **economy, premium economy**
- Maximum layovers: 2
- Direct flight preference: not required

**Hotel Constraints:**
- Maximum rate per night: **$250**
- Minimum rating: 3.5 stars
- Allowed classes: standard, comfort, upscale
- Required amenities: Free Wi-Fi, Breakfast included

**Budget Constraints:**
- Maximum total budget: **$4,000**
- Meal per diem: $75/day
- Ground transport: $75/day
- Incidentals: $35/day

**Approval Requirements:**
- Approval required: Yes
- Approver role: approving_manager
- Auto-approve threshold: Under $2,500

---

### Executive Policy
**Flight Constraints:**
- Maximum cost per person: **$1,500**
- Allowed classes: **economy, premium economy, business**
- Maximum layovers: 1
- Direct flight preference: **yes (preferred)**

**Hotel Constraints:**
- Maximum rate per night: **$400**
- Minimum rating: 4.0 stars
- Allowed classes: comfort, upscale, luxury
- Required amenities: Free Wi-Fi, Breakfast included, Gym

**Budget Constraints:**
- Maximum total budget: **$8,000**
- Meal per diem: $100/day
- Ground transport: $100/day
- Incidentals: $50/day

**Approval Requirements:**
- Approval required: Yes
- Approver role: approving_manager
- Auto-approve threshold: Under $5,000

---

## Analysis Instructions

When using `analyze_travel_compliance`:
1. **Identify the user's role** from the input parameters (employee/manager/executive)
2. **Parse the JSON** for flights and hotels
3. **Apply the corresponding policy limits** strictly based on role
4. **Filter out non-compliant options** based on:
   - Flight price exceeds max cost for role
   - Flight class not in allowed list for role
   - Hotel rate exceeds max per night for role
   - Total cost would exceed budget limit for role
5. **Return compliant options** with detailed explanations
6. **Explain violations** for filtered-out options

## Output Format

Return a structured response with:
- **Compliant Flights**: List of flights that meet policy (with prices and classes)
- **Compliant Hotels**: List of hotels that meet policy (with rates)
- **Filtered Out**: What was removed and why
- **Policy Applied**: Which role's policy was used
- **Recommendations**: Suggestions for the user

## Compliance Reporting

Always provide:
- ✅ **Compliant options** with clear indication they meet policy
- ❌ **Violations** with specific policy breaches explained
- 📊 **Policy limits** for transparency
- 💡 **Recommendations** for non-compliant selections

## Important Notes

- **Be strict**: Policy compliance is mandatory for corporate travel
- **Be transparent**: Always explain which policy rule applies
- **Be helpful**: Suggest alternatives when options don't comply
- **Consider role**: Different roles have different privileges
- **Escalation**: Trips exceeding limits require manager approval

Remember: The goal is to ensure all travel bookings comply with company policies while providing the best options within those constraints.