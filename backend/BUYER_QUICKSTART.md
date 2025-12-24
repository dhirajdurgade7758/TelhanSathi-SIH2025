# Buyer Auction System - Quick Start Guide

## 🎯 Overview
Complete buyer-side functionality for agricultural auction (NILAMI) marketplace. Buyers can search auctions, place competitive bids, track their bids, and manage purchases.

---

## 📍 Quick Navigation

### Main Pages
| Page | URL | Purpose |
|------|-----|---------|
| Dashboard | `/bidding/buyer/dashboard` | Overview of bids & stats |
| Browse Auctions | `/bidding/buyer/browse-auctions` | Search & discover auctions |
| Auction Details | `/bidding/buyer/auction/<id>` | View details & place bids |
| My Bids | `/bidding/buyer/my-bids` | Track all your bids |
| Won Auctions | `/bidding/buyer/won-auctions` | View completed purchases |
| Notifications | `/bidding/buyer/notifications` | Track auction updates |

---

## 🚀 Getting Started

### Step 1: Login as Buyer
```
Go to: http://localhost:3000/buyer/login
Username: buyer@example.com
Password: buyer_password
```

### Step 2: Access Buyer Dashboard
```
After login, you'll see:
- Statistics (Active Bids, Winning Bids, Total Bids, Won Auctions)
- Tab navigation (Browse, My Bids, Won)
- Featured auctions carousel
```

### Step 3: Browse Auctions
```
Option A: Click "Browse All" button
Option B: Go to /bidding/buyer/browse-auctions directly

Then:
1. Search by crop name (e.g., "Mustard")
2. Filter by district
3. Sort by price or bids
4. Click "Bid Now" on any auction
```

---

## 🎯 Key Features

### 1️⃣ Dashboard
- See all your statistics at a glance
- Quick access to featured auctions
- Unread notification badge
- Direct links to browse, bids, and won auctions

### 2️⃣ Browse Auctions
**Search & Filter:**
- By crop name
- By district
- Sort by newest, price, or bids
- Pagination (12 per page)

**Each Auction Shows:**
- Current price
- Quantity available
- Number of bids
- Quality grade
- Location
- Farmer name
- "Ending soon!" indicator

### 3️⃣ Auction Details & Bidding
**View:**
- Full auction information
- Farmer details
- Top 5 bids leaderboard
- Live countdown timer
- Description & storage info

**Place Bid:**
- Enter your bid amount
- See total value calculation
- Validates minimum requirements
- See success message after placing

### 4️⃣ My Bids
**Track All Your Bids:**
- Filter: All, Active, Winning, Closed
- See your bid price & total
- Know if you're leading (🏆)
- Quick link to view auction

### 5️⃣ Won Auctions
**View Your Purchases:**
- Winning price paid
- Total amount & quantity
- Farmer information
- Transaction timeline
- Days to completion

### 6️⃣ Notifications
**Stay Updated:**
- Real-time auction notifications
- Notifications for:
  - New bids placed
  - Auction closed
  - Counter offers
  - Auction extended
  - Auction cancelled
- Mark as read / Clear all
- Auto-refresh every 30 seconds

---

## 📊 Statistics & Metrics

### Dashboard Stats
```
Active Bids:      Auctions where you have an active bid
Winning Bids:     Bids where you have the highest price
Total Bids:       Total number of bids you've placed
Won Auctions:     Completed auctions you've won
Unread Notifs:    Number of unread notifications
```

### Bid Status Meanings
```
Active     - Auction still open, your bid is valid
Winning    - Your bid is the highest current bid
Bidding    - You have bid but not winning
Closed     - Auction has ended (you won or lost)
```

---

## 💡 Bidding Guide

### How to Place a Bid

**Step 1: Find Auction**
- Browse auctions or search by crop
- Click on auction card

**Step 2: Review Details**
- Check current price & requirements
- Read farmer info & description
- Look at top bids

**Step 3: Enter Your Bid**
- Must be ≥ current highest bid
- Must increase by minimum increment (usually ₹50)
- Enter amount in rupees per quintal

**Step 4: Place Bid**
- Click "🎯 Place Bid" button
- See success confirmation
- Check your bid is listed

### Bid Validation Rules
```
1. Bid ≥ Base Price (starting price)
2. Bid ≥ Current Highest Bid
3. Bid increase ≥ Minimum Increment (default ₹50/q)
4. Auction must be active
5. Time must not have expired
```

### Updating Your Bid
- If you want to increase your bid:
  1. Go back to auction
  2. Enter higher amount
  3. Click "Place Bid" again
  4. Your previous bid is replaced

---

## 🎨 Color Coding Guide

| Color | Meaning |
|-------|---------|
| 🟢 Green | Winning bid, active auction |
| 🟠 Orange | Active bid, not winning |
| 🔴 Red | Prices, important alerts |
| ⚫ Gray | Closed auction, inactive |
| 🟡 Yellow | Warnings, ending soon |

---

## ⏱️ Understanding Auction Times

```
Created At:     When auction was posted
Start Time:     When bidding opens
End Time:       When bidding closes
Time Remaining: How much time is left
                - Shows in hours/minutes/seconds
                - Updates live on page
```

### Time Formats
- "5h 30m remaining" - More than 1 hour left
- "45m 20s remaining" - Less than 1 hour left
- "⏰ Ending soon!" - Less than 5 minutes
- "Auction has ended" - Time expired

---

## 📱 Mobile Responsiveness

The buyer portal is fully mobile-optimized:
- Single column layout on mobile
- Touch-friendly buttons
- Auto-adjusting grids
- Fast loading
- Easy navigation

**Tested on:**
- iPhone 12/13/14
- Android phones
- Tablets
- Desktops

---

## 🔔 Notifications

### Notification Types

| Icon | Type | Meaning |
|------|------|---------|
| 📢 | New Bid | Someone placed higher bid |
| ⏹ | Closed | Auction ended |
| 💬 | Counter Offer | Farmer made counter offer |
| ⏱ | Extended | Auction time extended |
| ❌ | Cancelled | Auction cancelled |

### Managing Notifications
- **Unread Badge:** Shows count of unread
- **Mark All Read:** Mark everything as read
- **Clear All:** Clear all notifications
- **View Auction:** Click to go to auction
- **Auto-Refresh:** Updates every 30 seconds

---

## 📋 Workflow Examples

### Example 1: Win an Auction
```
1. Browse auctions → Find "Mustard" in Nashik
2. View details → See base price ₹5000/q, current bid ₹5200/q
3. Place bid → Enter ₹5300/q
4. Wait → Monitor countdown
5. Win! → Your bid remains highest until auction ends
6. Check → Go to "Won Auctions" to see purchase
```

### Example 2: Bid War
```
1. Place bid ₹5300/q on Mustard auction
2. Get notification: "New bid received ₹5400/q"
3. Increase bid to ₹5500/q
4. Another buyer bids ₹5600/q
5. You get notification again
6. Decide to bow out or bid higher
7. If highest when timer ends → You win!
```

### Example 3: Track Multiple Auctions
```
1. Place bids on 5 different auctions
2. Go to "My Bids" to see all
3. Filter "Winning" to see leading bids
4. Get notifications when others bid
5. Win 3 auctions, lose 2
6. View won auctions in "Won Auctions" section
```

---

## ❓ FAQ

**Q: Can I bid on the same auction twice?**
A: No, but you can update your bid amount.

**Q: What happens if time runs out?**
A: Auction closes. If your bid is highest, you won!

**Q: Can I cancel my bid?**
A: Currently no, but you can always bid higher or wait for auction to end.

**Q: How do I know if I'm winning?**
A: Check "My Bids" or look for 🏆 winning indicator.

**Q: What's the minimum bid increase?**
A: Typically ₹50/q, shown on auction details.

**Q: Do I get notifications?**
A: Yes! Automatically when others bid. Check "Notifications".

**Q: How long until I know if I won?**
A: Instantly when auction ends at end_time.

**Q: Can I see other bidders' names?**
A: No, only their bid prices in the top bids list.

**Q: What if multiple people bid the same price?**
A: First to place that bid wins (timestamp decides).

**Q: How do I contact the farmer?**
A: Farmer details shown on auction page. Further integration planned.

---

## 🛠️ Troubleshooting

### Issue: "Not authenticated" error
**Solution:** 
- Log in first at `/buyer/login`
- Make sure session is active
- Try clearing cookies and logging in again

### Issue: Bid won't place
**Solution:**
- Check bid meets minimum increment
- Verify bid ≥ current highest bid
- Ensure auction is still active (check countdown)
- Try refreshing page

### Issue: Notifications not updating
**Solution:**
- Page auto-refreshes every 30s
- Manually refresh with F5
- Check if browser notifications are enabled

### Issue: Can't see won auctions
**Solution:**
- Auction must be marked "completed" by farmer
- Check "My Bids" to see active status
- Wait for auction to fully end

### Issue: Price calculation wrong
**Solution:**
- Price shown is per quintal (per 100kg)
- Total = bid_price × quantity_quintals
- Check math on page (should auto-calculate)

---

## 🎓 Best Practices

### For Smart Bidding
1. **Research Prices:** Check multiple auctions first
2. **Bid Strategically:** Don't bid max immediately
3. **Monitor Countdown:** Watch for last-minute bids
4. **Set Your Limit:** Know max price before bidding
5. **Track Notifications:** React quickly to new bids
6. **Compare Farmers:** Check farmer location & reviews
7. **Check Quality:** Always verify quality grade

### For Avoiding Issues
1. **Read Full Details:** Don't skip description
2. **Verify Minimum:** Double-check bid minimum
3. **Check Time:** Don't bid right at end
4. **Update Carefully:** Don't accidentally over-bid
5. **Track Auctions:** Use "My Bids" to monitor
6. **Save Won Auctions:** Reference for future purchases

---

## 📞 Support

**Having issues?**
- Check this guide first
- Try the troubleshooting section
- Clear browser cache/cookies
- Log out and log in again
- Contact admin if problem persists

---

## 🎉 Ready to Start?

1. Go to: `http://localhost:3000/bidding/buyer/dashboard`
2. Login with your buyer account
3. Browse auctions
4. Place your first bid!

**Happy Bidding! 🌾💰**

---

*Last Updated: December 24, 2025*  
*Version: 1.0.0*  
*Platform: Telhan Sathi Agricultural Marketplace*
