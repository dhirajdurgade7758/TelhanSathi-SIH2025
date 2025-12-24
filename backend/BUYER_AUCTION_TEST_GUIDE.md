# Buyer Auction (NILAMI) System - Testing Guide

## System Overview
The buyer auction system allows authenticated buyers to:
- Browse live auctions with filters (crop, district)
- View detailed auction information
- Place bids with automatic validation
- Track bid history and status

## Files Modified

### Backend
- **`routes/bidding.py`** - Buyer auction endpoints (1044 lines)
  - `GET /bidding/buyer/auctions/api` - List auctions
  - `GET /bidding/buyer/auction/<id>/api` - Get auction details
  - `POST /bidding/buyer/auction/<id>/place-bid` - Place bid

### Frontend
- **`templates/buyer_dashboard.html`** - Integrated auction UI (1758 lines)
  - "Live Auctions" tab with filters and auction grid
  - Split-panel modal for viewing details and placing bids
  - Real-time bid validation and error handling

## Testing Steps

### 1. Setup & Prerequisites
```powershell
# Ensure backend is running
python app.py

# Verify database has auction data
# If needed, seed auctions:
python seed_market.py
```

### 2. Test Case: Browse Auctions
**Goal:** Verify auction list loads and displays correctly

1. Open browser and login as a buyer
2. Navigate to "🏪 Live Auctions" tab in buyer dashboard
3. Verify you see:
   - ✅ Auction cards with crop name, quantity, and price
   - ✅ "Current Highest: ₹X/Q" showing price or "no bid is initiated"
   - ✅ "Time Left" countdown
   - ✅ Filters for Crop Type and District
4. Try filtering by crop and district
5. Expected: Auction list updates based on filters

### 3. Test Case: View Auction Details
**Goal:** Verify modal opens with correct information and bid form

1. Click "View Details & Bid" on any auction
2. Verify modal shows (split-panel layout):
   
   **Left Panel (Auction Details):**
   - ✅ Crop name and quantity
   - ✅ Quality grade and base price
   - ✅ Location and farmer information
   - ✅ Bid history (top 5 bids with prices)

   **Right Panel (Bid Form):**
   - ✅ Current Highest Bid: ₹X/Q
   - ✅ Minimum Increment: ₹Y/Q
   - ✅ Minimum Required Bid: ₹Z/Q (calculated as current + increment)
   - ✅ Input field ready for bid amount
   - ✅ Submit button visible

### 4. Test Case: Place Valid Bid
**Goal:** Verify successful bid placement

1. In the bid form, enter: `<Current Highest> + <Minimum Increment>` or higher
2. Click "Submit Bid"
3. Expected:
   - ✅ Success message appears: "Bid placed successfully! Your bid has been recorded."
   - ✅ Modal closes after 1.5 seconds
   - ✅ Auction list refreshes
   - ✅ Your bid appears in the bid history

### 5. Test Case: Place Invalid Bid (Below Minimum)
**Goal:** Verify bid validation

1. In the bid form, enter a value LESS than "Minimum Required Bid"
2. Click "Submit Bid"
3. Expected:
   - ✅ Error message: "Bid must be at least ₹Z/Q"
   - ✅ Modal stays open
   - ✅ Error message appears in red above submit button

### 6. Test Case: Place Invalid Bid (Empty/Invalid)
**Goal:** Verify input validation

1. Leave bid amount empty or enter non-numeric value
2. Click "Submit Bid"
3. Expected:
   - ✅ Error message: "Please enter a valid bid amount"
   - ✅ Modal stays open

### 7. Test Case: Multiple Bids in Session
**Goal:** Verify system handles multiple bids

1. Place a bid on Auction A (see success message)
2. Modal closes and list refreshes
3. Click "View Details & Bid" on Auction B
4. Place a bid on Auction B
5. Expected:
   - ✅ Each bid succeeds independently
   - ✅ Bid history in each auction updates correctly
   - ✅ Modal resets for each new auction

### 8. Test Case: Bid Form Field Calculations
**Goal:** Verify minimum bid calculation is correct

1. For an auction with:
   - Current Highest: ₹100/Q
   - Minimum Increment: ₹5/Q
2. Open details modal
3. Expected Minimum Required Bid: ₹105/Q
4. Try bidding ₹104/Q → should show error
5. Try bidding ₹105/Q → should succeed

### 9. Test Case: Modal Close
**Goal:** Verify modal closes properly

1. Open auction details modal
2. Click ✕ button in top-right corner
3. Expected:
   - ✅ Modal closes
   - ✅ Auction list is still visible
   - ✅ Form fields are cleared
4. Open details again - modal should be fresh

### 10. Test Case: Auction with No Bids
**Goal:** Verify handling of auctions with no bids

1. Find an auction showing "no bid is initiated"
2. Click "View Details & Bid"
3. In modal, verify:
   - ✅ "Current Highest" shows the base price
   - ✅ "Minimum Required Bid" = base price + increment
   - ✅ You can place the first bid

## API Response Format (For Debugging)

### GET /bidding/buyer/auctions/api
```json
{
  "total": 25,
  "page": 1,
  "pages": 3,
  "auctions": [
    {
      "id": 1,
      "crop_name": "Wheat",
      "quantity_quintals": 100,
      "quality_grade": "A",
      "base_price": 2500,
      "highest_bid": 2650,
      "minimum_bid_increment": 50,
      "location": "Village A",
      "district": "District X",
      "bids_count": 3,
      "farmer_name": "John Doe",
      "farmer_location": "Farm Location",
      "time_remaining": 86400,
      "status": "active"
    }
  ]
}
```

### GET /bidding/buyer/auction/<id>/api
```json
{
  "id": 1,
  "crop_name": "Wheat",
  "quantity_quintals": 100,
  "quality_grade": "A",
  "base_price": 2500,
  "current_highest_bid": 2650,
  "minimum_bid_increment": 50,
  "location": "Village A",
  "district": "District X",
  "farmer_name": "John Doe",
  "farmer_location": "Farm Location",
  "bids_count": 3,
  "status": "active",
  "top_bids": [
    {"bid_price": 2650, "bid_total": 265000},
    {"bid_price": 2600, "bid_total": 260000}
  ]
}
```

### POST /bidding/buyer/auction/<id>/place-bid
**Request:**
```json
{
  "bid_amount": 2700
}
```

**Response (Success):**
```json
{
  "success": true
}
```

**Response (Error):**
```json
{
  "error": "Bid must be higher than current highest bid"
}
```

## Troubleshooting

### "Failed to load auctions: unknown error"
- Check browser console (F12 → Console tab)
- Ensure Flask backend is running
- Verify `/bidding/buyer/auctions/api` endpoint exists
- Check `data.error` vs `data.auctions` parsing

### Modal won't open
- Open browser console (F12)
- Ensure no JavaScript errors
- Verify `.view-auction-btn` class exists on buttons
- Check `data-auction-id` attribute value

### Bid submission fails
- Open browser console (F12) to see error
- Verify POST endpoint `/bidding/buyer/auction/<id>/place-bid`
- Check API response format (must have `{success: true}` or `{error: "message"}`)
- Ensure buyer is authenticated (session has `buyer_id_verified`)

### Bid form doesn't show calculations
- Clear browser cache (Ctrl+Shift+Delete)
- Refresh page (Ctrl+Shift+R - hard refresh)
- Check console for JavaScript errors
- Verify auction data has `current_highest_bid` and `minimum_bid_increment` fields

## Code Locations for Reference

### Modal Structure
- **File:** `buyer_dashboard.html`
- **Lines:** 590-630 (HTML structure)
- **Left panel (details):** `div#auctionDetails`
- **Right panel (bid form):** `div#bidFormContainer`
- **Bid form elements:**
  - `id="bidCurrentHighest"` - Current highest bid display
  - `id="bidMinIncrement"` - Minimum increment display
  - `id="bidMinRequired"` - Calculated minimum required bid
  - `id="bidAmount"` - Input field for bid amount
  - `id="bidError"` - Error message display
  - `id="submitBidBtn"` - Submit button

### Key JavaScript Functions
- **`loadAuctions()`** (lines 1374-1405) - Fetches auction list
- **`displayAuctions(data)`** (lines 1407-1467) - Renders auction cards
- **`viewAuctionDetails(auctionId)`** (lines 1486-1646) - Opens modal and populates form
- **`submitPlaceBid(auctionId, minimumBid)`** (lines 1648-1690) - Submits bid
- **`closeAuctionModal()`** (lines 1692-1696) - Closes modal

## Success Indicators

✅ All test cases pass
✅ No JavaScript errors in console
✅ Bid calculations are accurate
✅ Success messages appear and disappear
✅ Error messages are clear and helpful
✅ Modal opens/closes smoothly
✅ Auction list refreshes after bid
✅ Filters work correctly
✅ Multiple bids can be placed in sequence

---

**Last Updated:** After modal redesign to split-panel layout
**Status:** Ready for testing
