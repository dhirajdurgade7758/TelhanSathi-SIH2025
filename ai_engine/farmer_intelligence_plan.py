"""
TelhanSathi - Farmer Intelligence Dashboard
Multi-Market Price Analysis & Decision Support System
"""

import pandas as pd
import numpy as np
from io import StringIO

# Sample data from user
DATA = """Date,Commodity,Price,Market,Quantity
2023-01-01,Soybean,4968.75,Chennai,836
2023-01-02,Soybean,4745.98,Indore,893
2023-01-03,Soybean,4638.57,Surat,851
2023-01-04,Soybean,5315.52,Delhi,625
2023-01-05,Soybean,4877.32,Delhi,474
2023-01-06,Soybean,4719.52,Chennai,936
2023-01-07,Soybean,4737.27,Chennai,652
2023-01-08,Soybean,4840.89,Surat,480
2023-01-09,Soybean,4835.8,Mumbai,183
2023-01-10,Soybean,4974.13,Delhi,842
2023-01-11,Soybean,4996.87,Mumbai,990
2023-01-12,Soybean,4982.77,Mumbai,127
2023-01-13,Soybean,5260.55,Delhi,262
2023-01-14,Soybean,5284.69,Chennai,360
2023-01-15,Soybean,4497.96,Mumbai,523
2023-01-16,Soybean,5115.27,Surat,775
2023-01-17,Soybean,4953.14,Chennai,402
2023-01-18,Soybean,4979.29,Indore,109
2023-01-19,Soybean,4725.48,Indore,729"""

df = pd.read_csv(StringIO(DATA))
df['Date'] = pd.to_datetime(df['Date'])

print("\n" + "="*80)
print("TELHANSATHI - FARMER INTELLIGENCE SYSTEM")
print("What You Can Show to Farmers with Market Data")
print("="*80)

print("\n📊 FEATURE PLAN FOR FARMERS")
print("="*80)

# Feature 1: Best Market to Sell
print("\n✨ FEATURE 1: BEST MARKET RECOMMENDATION")
print("-" * 80)

market_analysis = df.groupby('Market').agg({
    'Price': ['mean', 'max', 'min', 'std'],
    'Quantity': 'mean',
    'Date': 'count'
}).round(2)

market_analysis.columns = ['Avg_Price', 'Max_Price', 'Min_Price', 'Price_Volatility', 'Avg_Quantity', 'Days_Data']

print("\n📍 MARKET-WISE ANALYSIS:")
print(market_analysis)

best_market = df.loc[df['Price'].idxmax()]
print(f"\n🎯 HIGHEST PRICE MARKET: {best_market['Market']}")
print(f"   Price: ₹{best_market['Price']:.2f}/quintal")
print(f"   Date: {best_market['Date'].date()}")
print(f"   Quantity Traded: {best_market['Quantity']} units")

avg_market = market_analysis.sort_values('Avg_Price', ascending=False)
print(f"\n💰 BEST AVERAGE PRICE MARKET: {avg_market.index[0]}")
print(f"   Average: ₹{avg_market.iloc[0]['Avg_Price']:.2f}/quintal")
print(f"   Range: ₹{avg_market.iloc[0]['Min_Price']:.2f} - ₹{avg_market.iloc[0]['Max_Price']:.2f}")

# Feature 2: Price Trends & Predictions
print("\n\n✨ FEATURE 2: PRICE TREND ANALYSIS")
print("-" * 80)

daily_avg = df.groupby('Date')['Price'].agg(['mean', 'min', 'max', 'std']).round(2)
print("\n📈 DAILY PRICE STATISTICS:")
print(daily_avg.head(10))

price_change = daily_avg['mean'].iloc[-1] - daily_avg['mean'].iloc[0]
price_change_pct = (price_change / daily_avg['mean'].iloc[0]) * 100

print(f"\n📊 TREND SUMMARY (Jan 1 - Jan 19):")
print(f"   Starting Price: ₹{daily_avg['mean'].iloc[0]:.2f}/quintal")
print(f"   Latest Price: ₹{daily_avg['mean'].iloc[-1]:.2f}/quintal")
print(f"   Change: ₹{price_change:.2f} ({price_change_pct:+.2f}%)")

if price_change > 0:
    print(f"   📈 TREND: UPWARD (Prices Rising - Good Time to Hold)")
else:
    print(f"   📉 TREND: DOWNWARD (Prices Falling - Consider Selling)")

# Feature 3: Quantity Demand Analysis
print("\n\n✨ FEATURE 3: DEMAND PATTERNS BY MARKET")
print("-" * 80)

quantity_by_market = df.groupby('Market')['Quantity'].agg(['mean', 'sum', 'min', 'max']).round(0)
quantity_by_market.columns = ['Avg_Qty', 'Total_Qty', 'Min_Qty', 'Max_Qty']
quantity_by_market = quantity_by_market.sort_values('Avg_Qty', ascending=False)

print("\n📦 DEMAND ANALYSIS (By Average Quantity):")
print(quantity_by_market)

high_demand_market = quantity_by_market.index[0]
print(f"\n🔥 HIGH DEMAND MARKET: {high_demand_market}")
print(f"   Average Daily Demand: {quantity_by_market.loc[high_demand_market, 'Avg_Qty']:.0f} units")
print(f"   Total Traded: {quantity_by_market.loc[high_demand_market, 'Total_Qty']:.0f} units")

# Feature 4: Volatility Analysis (Risk Assessment)
print("\n\n✨ FEATURE 4: PRICE VOLATILITY ANALYSIS")
print("-" * 80)

market_volatility = df.groupby('Market')['Price'].std().sort_values(ascending=False).round(2)
overall_volatility = df['Price'].std()

print("\n⚡ PRICE VOLATILITY (Risk Level):")
print(market_volatility)

print(f"\n📊 STABILITY ASSESSMENT:")
print(f"   Overall Volatility (Std Dev): ₹{overall_volatility:.2f}")
print(f"   Most Stable Market: {market_volatility.index[-1]} (₹{market_volatility.iloc[-1]:.2f})")
print(f"   Most Volatile Market: {market_volatility.index[0]} (₹{market_volatility.iloc[0]:.2f})")

# Feature 5: Time-based Recommendations
print("\n\n✨ FEATURE 5: TIMING RECOMMENDATION")
print("-" * 80)

daily_prices = df.groupby('Date')['Price'].mean()
latest_7day_avg = daily_prices.tail(7).mean()
overall_avg = daily_prices.mean()
price_percentile = (daily_prices.iloc[-1] / daily_prices.max()) * 100

print(f"\n⏰ CURRENT PRICE POSITION:")
print(f"   Overall Average Price: ₹{overall_avg:.2f}/quintal")
print(f"   Latest 7-Day Average: ₹{latest_7day_avg:.2f}/quintal")
print(f"   Current Price: ₹{daily_prices.iloc[-1]:.2f}/quintal")
print(f"   Position in Range: {price_percentile:.1f}% of max price")

if daily_prices.iloc[-1] >= overall_avg * 1.05:
    print(f"\n✅ RECOMMENDATION: SELL NOW")
    print(f"   Reason: Price is {((daily_prices.iloc[-1]/overall_avg - 1)*100):.1f}% above average")
elif daily_prices.iloc[-1] <= overall_avg * 0.95:
    print(f"\n⏳ RECOMMENDATION: WAIT OR HOLD")
    print(f"   Reason: Price is {((1 - daily_prices.iloc[-1]/overall_avg)*100):.1f}% below average")
else:
    print(f"\n➡️ RECOMMENDATION: MONITOR")
    print(f"   Reason: Price is near average, watch for trend changes")

# Feature 6: Multi-Market Opportunity
print("\n\n✨ FEATURE 6: MULTI-MARKET OPPORTUNITIES")
print("-" * 80)

latest_date = df['Date'].max()
latest_prices = df[df['Date'] == latest_date].sort_values('Price', ascending=False)

print(f"\n🎯 PRICES ON {latest_date.date()}:")
for idx, row in latest_prices.iterrows():
    print(f"   {row['Market']:12s}: ₹{row['Price']:8.2f}/qt  |  Quantity: {row['Quantity']:4.0f} units")

price_diff = latest_prices['Price'].max() - latest_prices['Price'].min()
price_diff_pct = (price_diff / latest_prices['Price'].min()) * 100

print(f"\n💡 ARBITRAGE OPPORTUNITY:")
print(f"   Highest Market: {latest_prices.iloc[0]['Market']} @ ₹{latest_prices.iloc[0]['Price']:.2f}")
print(f"   Lowest Market: {latest_prices.iloc[-1]['Market']} @ ₹{latest_prices.iloc[-1]['Price']:.2f}")
print(f"   Price Difference: ₹{price_diff:.2f} ({price_diff_pct:.1f}%)")

if price_diff > overall_avg * 0.05:
    print(f"   ⭐ SIGNIFICANT: Consider logistics to premium market")

# Feature 7: Storage & Holding Decision
print("\n\n✨ FEATURE 7: STORAGE & HOLDING DECISION")
print("-" * 80)

recent_trend = daily_prices.tail(3).mean() - daily_prices.head(3).mean()
print(f"\n📊 RECENT PRICE TREND (Last 3 days vs First 3 days):")
print(f"   Trend: {recent_trend:+.2f} rupees {'📈 UP' if recent_trend > 0 else '📉 DOWN'}")

if recent_trend > 0:
    print(f"\n💾 STORAGE RECOMMENDATION: HOLD IN STORAGE")
    print(f"   Reason: Prices trending upward")
    print(f"   Expected: Further price increase possible")
    print(f"   Cost: Storage cost should be < {recent_trend:.2f} per quintal")
else:
    print(f"\n🚚 STORAGE RECOMMENDATION: SELL NOW")
    print(f"   Reason: Prices trending downward")
    print(f"   Risk: Further price decline likely")

# Feature 8: Market Efficiency Score
print("\n\n✨ FEATURE 8: MARKET EFFICIENCY SCORE")
print("-" * 80)

print("\n🏆 MARKET RATINGS (Best for Selling):")
print("\nCriteria: Price × Demand × Stability")

market_scores = {}
for market in df['Market'].unique():
    market_df = df[df['Market'] == market]
    
    # Score = Average Price (40%) + Quantity (35%) + Stability (25%)
    price_score = (market_df['Price'].mean() / df['Price'].max()) * 40
    quantity_score = (market_df['Quantity'].mean() / df['Quantity'].max()) * 35
    stability_score = (1 - (market_df['Price'].std() / market_df['Price'].mean())) * 25 if market_df['Price'].std() > 0 else 25
    
    total_score = price_score + quantity_score + stability_score
    market_scores[market] = total_score

sorted_markets = sorted(market_scores.items(), key=lambda x: x[1], reverse=True)

rank = 1
for market, score in sorted_markets:
    print(f"   {rank}. {market:12s} - Score: {score:.1f}/100")
    rank += 1

# Feature 9: Risk vs Return Matrix
print("\n\n✨ FEATURE 9: RISK vs RETURN ANALYSIS")
print("-" * 80)

print("\n⚠️ RISK-RETURN MATRIX:")
print("\nMarket         | Avg Price | Risk (%) | Return Rating")
print("-" * 60)

for market in df['Market'].unique():
    market_df = df[df['Market'] == market]
    avg_price = market_df['Price'].mean()
    risk = (market_df['Price'].std() / avg_price) * 100
    
    if risk < 3:
        risk_label = "🟢 Low"
    elif risk < 5:
        risk_label = "🟡 Medium"
    else:
        risk_label = "🔴 High"
    
    return_label = "⭐⭐⭐" if avg_price > df['Price'].quantile(0.75) else "⭐⭐" if avg_price > df['Price'].median() else "⭐"
    
    print(f"{market:14s} | ₹{avg_price:7.2f}   | {risk:6.2f}% {risk_label:10s} | {return_label}")

# Feature 10: Actionable Insights
print("\n\n✨ FEATURE 10: ACTIONABLE INSIGHTS FOR FARMER")
print("-" * 80)

insights = []

# Insight 1: Best Market
best_avg_market = market_analysis['Avg_Price'].idxmax()
insights.append(f"🎯 SELL IN {best_avg_market}: Best average price (₹{market_analysis.loc[best_avg_market, 'Avg_Price']:.2f})")

# Insight 2: Stable Market
stable_market = market_volatility.idxmin()
insights.append(f"🛡️ STABLE OPTION: {stable_market} has lowest volatility (±₹{market_volatility[stable_market]:.2f})")

# Insight 3: High Demand
high_demand = quantity_by_market.index[0]
insights.append(f"📦 HIGH DEMAND: {high_demand} has strong buyer interest ({quantity_by_market.loc[high_demand, 'Avg_Qty']:.0f} units/day)")

# Insight 4: Timing
if price_change > 0:
    insights.append(f"⏰ TIMING: Prices are rising {price_change_pct:+.1f}% - good time to sell")
else:
    insights.append(f"⏰ TIMING: Prices are falling - hold if possible or sell to best market")

# Insight 5: Strategy
if price_diff_pct > 5:
    insights.append(f"💡 STRATEGY: Price difference across markets is {price_diff_pct:.1f}% - explore logistics to premium market")

print("\n🎓 FARMER INSIGHTS:")
for i, insight in enumerate(insights, 1):
    print(f"   {i}. {insight}")

# Summary
print("\n\n" + "="*80)
print("✅ SUMMARY: WHAT YOU CAN SHOW FARMERS")
print("="*80)

features = [
    "1. Best Market to Sell (by price & demand)",
    "2. Price Trend & Forecast",
    "3. Demand Patterns Across Markets",
    "4. Price Volatility & Risk Assessment",
    "5. Timing Recommendations (Sell Now / Hold / Wait)",
    "6. Multi-Market Price Comparison",
    "7. Storage & Holding Decisions",
    "8. Market Efficiency Ratings",
    "9. Risk vs Return Analysis",
    "10. Actionable Selling Strategies"
]

print("\nFARMER-FACING FEATURES:")
for feature in features:
    print(f"   ✓ {feature}")

print("\n" + "="*80)
print("💡 NEXT STEPS FOR TELHANSATHI:")
print("="*80)

next_steps = [
    "1. Build Mobile App showing these 10 features",
    "2. Send Daily SMS alerts: Best market + Price trend",
    "3. Weekly Reports: Multi-market comparison",
    "4. Notifications: When price hits target",
    "5. Calculator: Revenue if sold to each market",
    "6. Historical Charts: Price movements over weeks/months",
    "7. Recommendations: Storage vs Sell decision",
    "8. Community: Share best selling strategies",
    "9. API: Integrate with banking/government schemes",
    "10. Subsidies: Show eligible schemes by location/crop"
]

print("\nDEVELOPMENT ROADMAP:")
for step in next_steps:
    print(f"   📌 {step}")

print("\n" + "="*80)
