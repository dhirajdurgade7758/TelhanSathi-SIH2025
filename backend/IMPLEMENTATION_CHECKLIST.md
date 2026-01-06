# Implementation Checklist - Farmer Auction Hindi Conversion

## Overview
This checklist will help you systematically convert all 5 farmer auction pages to Hindi using the translation guides provided.

**Total Pages:** 5
**Estimated Time:** 3-5 hours for full conversion + 1-2 hours testing
**Difficulty:** Medium (straightforward text replacement with HTML structure preservation)

---

## Pre-Implementation

- [ ] Review all three reference documents:
  - `FARMER_AUCTION_HINDI_CONVERSION.md` (comprehensive guide)
  - `HINDI_CONVERSION_SUMMARY.md` (overview)
  - `TRANSLATION_QUICK_REFERENCE.md` (dictionary)

- [ ] Backup original files:
  - [ ] Back up `farmer_create_auction.html`
  - [ ] Back up `farmer_edit_auction.html`
  - [ ] Back up `farmer_auction_dashboard.html`
  - [ ] Back up `farmer_auction_details.html`
  - [ ] Back up `farmer_auction_bids.html`

- [ ] Set up your editor:
  - [ ] Open each file in VS Code
  - [ ] Enable Find & Replace (Ctrl+H)
  - [ ] Consider using Multi-file Find & Replace for consistency

---

## File 1: farmer_create_auction.html

### Section 1: Page Title & Headers
- [ ] Line 3: Change `Block title` from "Create Auction" to "नीलामी बनाएं"
- [ ] Line 8: Change h1 from "🎯 Create New Auction" to "🎯 नई नीलामी बनाएं"
- [ ] Line 9: Change subheading text completely

### Section 2: Crop Information
- [ ] Line 15: Change legend from "Crop Information" to "फसल की जानकारी"
- [ ] Line 18: Change label from "Crop Type *" to "फसल का प्रकार *"
- [ ] Line 19: Change placeholder from "Select Crop" to "फसल चुनें"
- [ ] Lines 20-25: Crop options (keep English as values, update display text if mixed)
- [ ] Line 30: Change label from "Quantity (Quintals) *" to "मात्रा (क्विंटल) *"
- [ ] Line 32: Change help text from "1 quintal = 100 kg" to "1 क्विंटल = 100 किग्रा"
- [ ] Line 36: Change label from "Quality Grade" to "गुणवत्ता ग्रेड"
- [ ] Lines 38-41: Quality grade options
  - [ ] "Standard" → "मानक"
  - [ ] "Grade A - Premium" → "ग्रेड ए - प्रीमियम"
  - [ ] "Grade B - Good" → "ग्रेड बी - अच्छी"
  - [ ] "Grade C - Fair" → "ग्रेड सी - सामान्य"
- [ ] Line 45: Change label from "Description (Optional)" to "विवरण (वैकल्पिक)"
- [ ] Line 46: Change placeholder text

### Section 3: Pricing & Bidding
- [ ] Line 52: Change legend to "मूल्य निर्धारण और बोली लगाना"
- [ ] Line 57: Change label to "आधार मूल्य (₹/क्विंटल) *"
- [ ] Line 59: Change help text to "बोली लगाने के लिए शुरुआती मूल्य"
- [ ] Line 63: Change label to "न्यूनतम बोली वृद्धि (₹)"
- [ ] Line 65: Change help text to "प्रति बोली न्यूनतम वृद्धि"

### Section 4: Auction Duration
- [ ] Line 71: Change legend to "नीलामी की अवधि"
- [ ] Line 76: Change label to "नीलामी की अवधि (घंटे) *"
- [ ] Line 77: Change placeholder to "अवधि चुनें"
- [ ] Lines 78-86: Duration options (1 घंटा, 2 घंटे, etc.)
- [ ] Line 90: Change label to "नीलामी शुरुआत समय"
- [ ] Line 91: Keep "Now" OR change to "अभी"
- [ ] Line 92: Change help text to "नीलामी सृजन के तुरंत बाद शुरू होती है"

### Section 5: Location & Logistics
- [ ] Line 98: Change legend to "स्थान और लॉजिस्टिक्स"
- [ ] Line 103: Change label to "खेत का स्थान *"
- [ ] Line 104: Change placeholder to "पता"
- [ ] Line 108: Change label to "जिला *"
- [ ] Line 113: Change label to "राज्य"
- [ ] Line 114: Change value to "महाराष्ट्र"
- [ ] Line 118: Change label to "भंडारण स्थान (वैकल्पिक)"
- [ ] Line 119: Change placeholder
- [ ] Line 124: Change label to "कटाई की तारीख (वैकल्पिक)"

### Section 6: Photos Section
- [ ] Line 130: Change legend to "📸 तिलहन फसल की तस्वीरें"
- [ ] Line 131: Change description text
- [ ] Lines 135-172: Update all 4 photo upload group labels and descriptions:
  - [ ] "Photo 1 (Required)" → "फोटो 1 (आवश्यक)"
  - [ ] "Click to upload" → "क्लिक करके अपलोड करें"
  - [ ] "Main harvest photo - required for listing"
  - [ ] Similar updates for Photos 2, 3, 4

### Section 7: Form Actions
- [ ] Line 177: Change button text to "🎯 नीलामी बनाएं"
- [ ] Line 180: Change button text to "रद्द करें"

**Status:** [ ] Complete

---

## File 2: farmer_edit_auction.html

### Section 1: Page Title & Header
- [ ] Line 3: Change block title to "नीलामी संपादित करें - तेलहान साथी"
- [ ] Line 125: Change back button text (if visible)
- [ ] Line 126: Change h1 to "✏️ नीलामी संपादित करें"
- [ ] Line 127: Change subheading

### Section 2: Crop Information
- [ ] Line 132: Change legend to "फसल की जानकारी"
- [ ] Lines 135-142: Update all crop labels and options (same as file 1)

### Section 3: Quantity & Quality
- [ ] Line 147: Change label to "मात्रा (क्विंटल) *"
- [ ] Line 149: Change help text to "1 क्विंटल = 100 किग्रा"
- [ ] Line 153: Change label to "गुणवत्ता ग्रेड"
- [ ] Lines 154-157: Update quality grade options

### Section 4: Description
- [ ] Line 162: Change label to "विवरण (वैकल्पिक)"
- [ ] Line 163: Change placeholder to "अपनी फसल का वर्णन करें..."

### Section 5: Pricing
- [ ] Line 168: Change legend to "मूल्य निर्धारण"
- [ ] Line 172: Change label to "आधार मूल्य (₹/क्विंटल) *"
- [ ] Line 178: Change label to "न्यूनतम बोली वृद्धि (₹/क्विंटल)"

### Section 6: Location & Details
- [ ] Line 184: Change legend to "स्थान और विवरण"
- [ ] Lines 188-209: Update all location-related labels and placeholders (similar to File 1)

### Section 7: Photos Section
- [ ] Line 214: Change legend to "📸 फसल की तस्वीरें"
- [ ] Line 215: Change description
- [ ] Lines 220-263: Update all photo labels and descriptions with "मौजूदा" for current photo indicators

### Section 8: Form Actions
- [ ] Line 267: Change button to "💾 परिवर्तन सहेजें"
- [ ] Line 268: Change button to "← रद्द करें"

### Section 9: JavaScript Messages
- [ ] Update JS notification: "✓ नई तस्वीर चुनी गई (वर्तमान को बदल देगी)"
- [ ] Update button text: "⏳ सहेज रहे हैं..."
- [ ] Update error message: "नीलामी को अपडेट करने में त्रुटि"

**Status:** [ ] Complete

---

## File 3: farmer_auction_dashboard.html

### Section 1: Page Title & Header
- [ ] Line 3: Change block title to "किसान नीलामी डैशबोर्ड - तेलहान साथी"
- [ ] Line 8: Change h1 to "🎯 नीलामी (बोली) डैशबोर्ड"
- [ ] Line 10: Change button to "➕ नई नीलामी बनाएं"
- [ ] Line 13: Change subheading

### Section 2: Tab Navigation
- [ ] Line 17: Change tab button to "📊 सारांश"
- [ ] Line 20: Change tab button to "🎯 मेरी नीलामियाँ"

### Section 3: Statistics Cards
- [ ] Line 27: Change stat label to "सक्रिय नीलामियाँ"
- [ ] Line 33: Change stat label to "पूर्ण"
- [ ] Line 39: Change stat label to "सर्वश्रेष्ठ मूल्य"
- [ ] Line 45: Change stat label to "कुल बोलियाँ"

### Section 4: My Auctions Section
- [ ] Line 53: Change heading to "मेरी नीलामियाँ"
- [ ] Lines 57-66: Update all filter buttons:
  - [ ] "All" → "सभी"
  - [ ] "⏳ Active" → "⏳ सक्रिय"
  - [ ] "✅ Completed" → "✅ पूर्ण"
  - [ ] "❌ Cancelled" → "❌ रद्द"
- [ ] Line 71: Change button to "🔄 ताज़ा करें"
- [ ] Line 75: Change loading text to "नीलामियाँ लोड हो रही हैं..."

### Section 5: Manage Modal
- [ ] Line 78: Change modal heading to "नीलामी प्रबंधित करें"
- [ ] Lines 85-106: Update all manage button labels and descriptions:
  - [ ] "✅ Accept Bid" → "✅ बोली स्वीकार करें"
  - [ ] "Accept the highest bid" → "सर्वोच्च बोली स्वीकार करें"
  - [ ] "💬 Counter Offer" → "💬 प्रतिवर्ती प्रस्ताव"
  - [ ] etc.

**Status:** [ ] Complete

---

## File 4: farmer_auction_details.html

### Section 1: Page Title & Header
- [ ] Line 3: Change block title to "नीलामी विवरण - तेलहान साथी"
- [ ] Line 7: Keep/update back button to "← वापस"
- [ ] Line 8: Change h1 to "🎯 नीलामी विवरण"
- [ ] Line 14: Change edit button text to "✏️ संपादित करें"

### Section 2: Won Auction Section
- [ ] Line 20: Change heading to "🏆 नीलामी जीत गई!"
- [ ] Line 21: Change text to "आपकी नीलामी सफलतापूर्वक पूर्ण हुई है।"
- [ ] Lines 25-27: Update winning price labels
- [ ] Lines 30-64: Update all buyer detail labels (Company Name, Contact Person, etc.)

### Section 3: Auction Details Section
- [ ] Lines 74-116: Update all detail item labels:
  - [ ] "📦 Quantity" → "📦 मात्रा"
  - [ ] "💰 Base Price" → "💰 आधार मूल्य"
  - [ ] etc.

### Section 4: Photos Section
- [ ] Line 124: Change heading to "📸 तिलहन फसल की तस्वीरें"
- [ ] Lines 131-149: Update photo labels:
  - [ ] "Main Harvest" → "मुख्य फसल"
  - [ ] "Detail View" → "विस्तृत दृश्य"
  - [ ] "Quality/Grade" → "गुणवत्ता/ग्रेड"
  - [ ] "Storage/Packaging" → "भंडारण/पैकेजिंग"

### Section 5: Description Section
- [ ] Line 155: Change heading to "📝 विवरण"

### Section 6: Action Buttons
- [ ] Line 163: Change button to "📊 सभी बोलियाँ देखें"
- [ ] Line 168: Change button to "⚙️ नीलामी प्रबंधित करें"
- [ ] Line 173: Change button to "← वापस जाएं"

### Section 7: Counter Offers Section
- [ ] Line 177: Change heading to "💬 भेजे गए प्रतिवर्ती प्रस्ताव"
- [ ] Lines 180-183: Update filter buttons:
  - [ ] "All" → "सभी"
  - [ ] "Pending" → "लंबित"
  - [ ] "Accepted" → "स्वीकृत"
  - [ ] "Rejected" → "अस्वीकृत"
- [ ] Line 190: Change empty state to "अभी तक कोई प्रतिवर्ती प्रस्ताव नहीं भेजा गया"

### Section 8: Manage Modal & Counter Offer Modal
- [ ] Update all modal headings and button text (similar to File 3)

**Status:** [ ] Complete

---

## File 5: farmer_auction_bids.html

### Section 1: Page Title & Header
- [ ] Line 3: Change block title to "नीलामी बोलियाँ - तेलहान साथी"
- [ ] Line 8: Keep/update back button to "← वापस"
- [ ] Line 9: Change h1 to "📊 आपकी नीलामी के लिए बोलियाँ"

### Section 2: Bids List & Messages
- [ ] Line 15: Change loading text to "बोलियाँ लोड हो रही हैं..."
- [ ] Line 60: Change empty state to "अभी तक कोई बोली शुरू नहीं की गई है"
- [ ] Lines 67-76: Update bid details labels:
  - [ ] "Bid Price" → "बोली मूल्य"
  - [ ] "Total Amount" → "कुल राशि"
  - [ ] "Bid Date" → "बोली की तारीख"
- [ ] Lines 90-91: Update error messages:
  - [ ] "Failed to load bids" → "बोलियों को लोड करने में विफल"
  - [ ] "Please refresh the page and try again" → "कृपया पृष्ठ को ताज़ा करें और फिर से प्रयास करें"

### Section 3: Bid Status Labels (in JavaScript)
- [ ] Update status display in JavaScript for:
  - [ ] "PENDING" → "लंबित"
  - [ ] "ACCEPTED" → "स्वीकृत"
  - [ ] "REJECTED" → "अस्वीकृत"

**Status:** [ ] Complete

---

## Testing Checklist

### Desktop Testing
- [ ] File 1 (Create):
  - [ ] All form labels visible and in Hindi
  - [ ] All buttons display correctly
  - [ ] Form is functional
  - [ ] Help text is readable

- [ ] File 2 (Edit):
  - [ ] All fields populated with Hindi labels
  - [ ] Photo previews work
  - [ ] Form submission works

- [ ] File 3 (Dashboard):
  - [ ] Tabs switch correctly
  - [ ] Filter buttons work
  - [ ] Statistics display
  - [ ] Modal opens/closes properly

- [ ] File 4 (Details):
  - [ ] All details display correctly
  - [ ] Photos load properly
  - [ ] Modals function correctly
  - [ ] Buttons are responsive

- [ ] File 5 (Bids):
  - [ ] Bids load and display
  - [ ] Empty state shows correctly
  - [ ] Error handling works

### Mobile Testing
- [ ] Test on device at 480px width:
  - [ ] Text doesn't overflow
  - [ ] Buttons are clickable
  - [ ] Layout is responsive
  - [ ] Hindi text displays properly

- [ ] Test on tablet at 768px width:
  - [ ] Grid layouts work
  - [ ] Forms are usable
  - [ ] Modals appear correctly

### Browser Testing
- [ ] Chrome: [ ] Full functionality
- [ ] Firefox: [ ] Full functionality
- [ ] Safari: [ ] Full functionality
- [ ] Edge: [ ] Full functionality

### Content Verification
- [ ] All English text replaced with Hindi
- [ ] No "Select" placeholders remaining in English
- [ ] All buttons have Hindi text
- [ ] All labels are in Hindi
- [ ] Help text is in Hindi
- [ ] Error/success messages are in Hindi
- [ ] Emoji are preserved

### Functionality Verification
- [ ] Form validation still works
- [ ] File uploads work
- [ ] API calls still function
- [ ] Modals open/close correctly
- [ ] Tabs switch properly
- [ ] Filter buttons work
- [ ] All JavaScript functions execute properly
- [ ] No console errors

---

## Post-Implementation

- [ ] **Code Review:**
  - [ ] Check all HTML is valid
  - [ ] No broken tags or attributes
  - [ ] No orphaned code

- [ ] **Performance Check:**
  - [ ] Page load times acceptable
  - [ ] No rendering issues
  - [ ] Mobile performance good

- [ ] **QA Verification:**
  - [ ] All 5 files fully translated
  - [ ] No English text visible on any page
  - [ ] Consistency across all files
  - [ ] Special characters (ँ, ं, ः) display correctly

- [ ] **Documentation:**
  - [ ] Update any relevant README files
  - [ ] Document any special handling needed
  - [ ] Note any patterns for future translations

- [ ] **Git/Version Control:**
  - [ ] Commit changes with clear message
  - [ ] Tag version if appropriate
  - [ ] Create pull request if applicable

---

## Estimated Time Breakdown

| Task | Time |
|------|------|
| File 1 (Create) | 45 min |
| File 2 (Edit) | 40 min |
| File 3 (Dashboard) | 35 min |
| File 4 (Details) | 40 min |
| File 5 (Bids) | 20 min |
| Testing | 90 min |
| **Total** | **~4.5 hours** |

---

## Notes & Tips

1. **Use Find & Replace Wisely:**
   - Replace specific phrases, not single words
   - Review each replacement before confirming
   - Use context to avoid false matches

2. **Preserve HTML Structure:**
   - Don't modify any HTML tags
   - Keep all attributes intact
   - Ensure class names and IDs remain unchanged

3. **Testing is Critical:**
   - Test each file after translating
   - Don't wait until all files are done
   - Check mobile view for each file

4. **Consistency:**
   - Use the provided translation dictionary
   - Don't create new translations mid-way
   - Reference the guides for consistency

5. **Common Pitfalls to Avoid:**
   - Don't translate placeholder text in attributes
   - Don't translate code variable names
   - Don't translate CSS class names or IDs
   - Don't translate URL paths or API endpoints

---

**Last Updated:** January 2026
**Version:** 1.0
**Status:** Ready for Implementation
