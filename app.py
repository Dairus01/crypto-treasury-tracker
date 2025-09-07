import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Crypto Treasury Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-box {border-radius:12px;padding:16px;margin:8px 0;background:#0f1116;border:2px solid rgba(255,255,255,0.08)}
    .metric-title {font-size:0.95rem;color:#cfd3dc;margin:0 0 6px 0}
    .metric-value {font-size:1.6rem;font-weight:700;color:#fff;margin:0}
    .metric-green {border-color:#22c55e40; box-shadow:0 0 0 1px #22c55e20 inset}
    .metric-blue {border-color:#3b82f640; box-shadow:0 0 0 1px #3b82f620 inset}
    .metric-orange {border-color:#f59e0b40; box-shadow:0 0 0 1px #f59e0b20 inset}
    .metric-purple {border-color:#8b5cf640; box-shadow:0 0 0 1px #8b5cf620 inset}
    .metric-teal {border-color:#14b8a640; box-shadow:0 0 0 1px #14b8a620 inset}
    .profit { color: #00ff88; font-weight: bold; }
    .loss { color: #ff4444; font-weight: bold; }
    .stAlert { margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

class TreasuryTracker:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv('COINGECKO_API_KEY')
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({'X-CG-API-KEY': self.api_key})
        
        # Cache data
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour
        # FX rates cache (USD base)
        self.fx_rates = {"USD": 1.0}
        
    def get_treasury_data(self, coin_id: str) -> Optional[Dict]:
        """Fetch treasury data for a specific coin from CoinGecko API"""
        cache_key = f"treasury_{coin_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                return data
        
        try:
            url = f"{self.base_url}/companies/public_treasury/{coin_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # Cache the data
                self.cache[cache_key] = (time.time(), data)
                return data
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return None
    
    def get_exchange_rates(self) -> Dict:
        """Get current exchange rates for currency conversion"""
        cache_key = "exchange_rates"
        
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                return data
        
        try:
            url = f"{self.base_url}/exchange_rates"
            response = self.session.get(url)
            
            if response.status_code == 200:
                rates = response.json()['rates']
                self.cache[cache_key] = (time.time(), rates)
                return rates
            else:
                return {'usd': {'value': 1.0}}
                
        except Exception as e:
            return {'usd': {'value': 1.0}}

    def get_usd_fx_rates(self) -> Dict[str, float]:
        """Fetch USD base fiat FX rates for common currencies.
        Falls back to 1.0 for USD if API is unavailable.
        """
        cache_key = "usd_fx_rates"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                self.fx_rates = data
                return data
        try:
            # Free, no-key USD base FX API
            resp = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
            if resp.status_code == 200:
                payload = resp.json()
                if payload.get("result") == "success" and "rates" in payload:
                    rates = payload["rates"]
                    normalized = {
                        "USD": 1.0,
                        "EUR": float(rates.get("EUR", 0)),
                        "GBP": float(rates.get("GBP", 0)),
                        "JPY": float(rates.get("JPY", 0)),
                        "CAD": float(rates.get("CAD", 0)),
                        "AUD": float(rates.get("AUD", 0)),
                    }
                    # Ensure sane fallbacks
                    for k in list(normalized.keys()):
                        if not normalized[k]:
                            normalized[k] = 1.0 if k == "USD" else 0.0
                    self.cache[cache_key] = (time.time(), normalized)
                    self.fx_rates = normalized
                    return normalized
        except Exception:
            pass
        # Fallback
        fallback = {"USD": 1.0, "EUR": 0.0, "GBP": 0.0, "JPY": 0.0, "CAD": 0.0, "AUD": 0.0}
        self.fx_rates = fallback
        self.cache[cache_key] = (time.time(), fallback)
        return fallback
    
    def process_treasury_data(self, data: Dict, coin_id: str) -> pd.DataFrame:
        """Process raw treasury data into a clean DataFrame"""
        if not data or 'companies' not in data:
            return pd.DataFrame()
        
        companies = []
        for company in data['companies']:
            companies.append({
                'Name': company.get('name', 'Unknown'),
                'Symbol': company.get('symbol', 'N/A'),
                'Country': company.get('country', 'Unknown'),
                'Total Holdings': company.get('total_holdings', 0),
                'Entry Value': company.get('total_entry_value_usd', 0),
                'Current Value': company.get('total_current_value_usd', 0),
                '% of Total Supply': company.get('percentage_of_total_supply', 0)
            })
        
        df = pd.DataFrame(companies)
        if not df.empty:
            # Compute PnL per company
            df['PnL'] = (df['Current Value'] - df['Entry Value']).fillna(0)
            df['PnL %'] = df.apply(lambda r: ((r['PnL'] / r['Entry Value']) * 100) if r['Entry Value'] and r['Entry Value'] != 0 else 0, axis=1)
            df = df.sort_values('Total Holdings', ascending=False)
        
        return df
    
    def format_currency(self, value_usd: float, currency: str = 'USD') -> str:
        """Format amounts (provided in USD) into selected fiat with suffixes."""
        if pd.isna(value_usd) or value_usd == 0:
            symbol_map = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "C$", "AUD": "A$"}
            return f"{symbol_map.get(currency, '$')}0"
        rate = self.fx_rates.get(currency, 1.0)
        converted = value_usd * rate
        symbol_map = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "C$", "AUD": "A$"}
        prefix = symbol_map.get(currency, "$")
        abs_value = abs(converted)
        if abs_value >= 1e9:
            return f"{prefix}{converted/1e9:.2f}B"
        elif abs_value >= 1e6:
            return f"{prefix}{converted/1e6:.2f}M"
        elif abs_value >= 1e3:
            return f"{prefix}{converted/1e3:.2f}K"
        else:
            return f"{prefix}{converted:.2f}"
    
    def format_crypto_amount(self, amount: float, coin: str) -> str:
        """Format crypto amounts with proper precision"""
        if pd.isna(amount) or amount == 0:
            return "0"
        
        if coin == 'BTC':
            return f"{amount:,.0f} BTC"
        elif coin == 'ETH':
            return f"{amount:,.0f} ETH"
        else:
            return f"{amount:,.2f} {coin}"

    def render_metric(self, title: str, value: str, color_class: str) -> None:
        """Render a styled metric box similar to the reference design."""
        st.markdown(
            f"""
            <div class='metric-box {color_class}'>
                <div class='metric-title'>{title}</div>
                <p class='metric-value'>{value}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

def main():
    st.markdown('<h1 class="main-header">💰 Crypto Treasury Tracker</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <p style='font-size: 1.2rem; color: #666;'>
            Track Bitcoin and Ethereum holdings of public companies with real-time PnL analysis
        </p>

    </div>
    """, unsafe_allow_html=True)
    
    # Initialize tracker
    tracker = TreasuryTracker()
    
    # Sidebar controls
    st.sidebar.header("🎛️ Controls")
    
    # Asset selection
    selected_asset = st.sidebar.selectbox(
        "Select Asset",
        ["Bitcoin (BTC)", "Ethereum (ETH)", "Both"],
        index=0
    )
    
    # Currency selection
    currencies = {
        'USD': 'USD',
        'EUR': 'EUR', 
        'GBP': 'GBP',
        'JPY': 'JPY',
        'CAD': 'CAD',
        'AUD': 'AUD'
    }
    
    selected_currency = st.sidebar.selectbox(
        "Display Currency",
        list(currencies.keys()),
        index=0
    )
    

    
    # Fetch data
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Load FX rates early so all views convert correctly
    tracker.get_usd_fx_rates()

    # Data loading
    with st.spinner("Fetching treasury data..."):
        btc_data = None
        eth_data = None
        
        if selected_asset in ["Bitcoin (BTC)", "Both"]:
            btc_data = tracker.get_treasury_data("bitcoin")
        
        if selected_asset in ["Ethereum (ETH)", "Both"]:
            eth_data = tracker.get_treasury_data("ethereum")
    
    # Display data
    if selected_asset == "Bitcoin (BTC)" and btc_data:
        display_bitcoin_data(tracker, btc_data, selected_currency)
    elif selected_asset == "Ethereum (ETH)" and eth_data:
        display_ethereum_data(tracker, eth_data, selected_currency)
    elif selected_asset == "Both" and (btc_data or eth_data):
        display_combined_data(tracker, btc_data, eth_data, selected_currency)
    else:
        st.warning("No data available. Please check your API key or try again later.")
    
    # Footer removed as requested

def display_bitcoin_data(tracker, data, currency):
    """Display Bitcoin treasury data"""
    st.header("📊 Bitcoin Treasury Holdings")
    
    # Overall stats
    if 'total_holdings' in data:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # Handle both dictionary and direct value formats
            if isinstance(data['total_holdings'], dict):
                total_btc = data['total_holdings'].get('bitcoin', 0)
            else:
                total_btc = data['total_holdings']
            tracker.render_metric("Total BTC Held", f"{total_btc:,.0f} BTC", "metric-green")
        
        with col2:
            total_value = data.get('total_value_usd', 0)
            tracker.render_metric("Total Value", tracker.format_currency(total_value, currency), "metric-blue")
        
        with col3:
            total_companies = len(data.get('companies', []))
            avg_btc = (total_btc / total_companies) if total_companies else 0
            tracker.render_metric("Avg BTC / Company", f"{avg_btc:,.0f}", "metric-orange")
        
        with col4:
            tracker.render_metric("Companies Tracked", f"{total_companies}", "metric-purple")

        with col5:
            # Market cap dominance approximated as companies' share of BTC supply
            dominance = 0.0
            try:
                # Prefer API-provided percentages per company
                companies = data.get('companies', [])
                if companies:
                    dominance = sum([c.get('percentage_of_total_supply', 0) or 0 for c in companies])
                elif total_btc:
                    dominance = (total_btc / 21_000_000) * 100
            except Exception:
                dominance = 0.0
            tracker.render_metric("Market Cap Dominance", f"{dominance:.2f}%", "metric-teal")
    
    # Process data
    df = tracker.process_treasury_data(data, "bitcoin")
    
    if not df.empty:
        # Display table
        st.subheader("🏢 Company Holdings")
        
        # Format display columns
        display_df = df.copy()
        display_df['Total Holdings'] = display_df['Total Holdings'].apply(lambda x: f"{x:,.0f}")
        display_df['Entry Value'] = display_df['Entry Value'].apply(lambda v: tracker.format_currency(v, currency))
        display_df['Current Value'] = display_df['Current Value'].apply(lambda v: tracker.format_currency(v, currency))
        display_df['PnL'] = display_df['PnL'].apply(lambda v: tracker.format_currency(v, currency))
        display_df['PnL %'] = display_df['PnL %'].apply(lambda x: f"{x:.2f}%")
        display_df['% of Total Supply'] = display_df['% of Total Supply'].apply(lambda x: f"{x:.3f}%")
        
        st.dataframe(display_df, use_container_width=True)

        # Charts row
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            # Donut: Companies vs Others share of BTC supply
            companies_share = (df['% of Total Supply'].sum()) if '% of Total Supply' in df.columns else (total_btc / 21_000_000 * 100 if total_btc else 0)
            companies_share = max(0.0, min(100.0, companies_share))
            others_share = 100 - companies_share
            pie_fig = px.pie(values=[companies_share, others_share], names=['Public Companies', 'Others'], hole=0.6,
                              title='Share of BTC Supply (Companies vs Others)')
            pie_fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(pie_fig, use_container_width=True)
        with chart_col2:
            # Top companies by current value
            top_df = df.nlargest(10, 'Current Value')
            bar_fig = px.bar(top_df, x='Name', y='Current Value', title='Top Public Companies Holding BTC')
            bar_fig.update_yaxes(title_text=f"Value ({currency})")
            st.plotly_chart(bar_fig, use_container_width=True)

def display_ethereum_data(tracker, data, currency):
    """Display Ethereum treasury data"""
    st.header("📊 Ethereum Treasury Holdings")
    
    # Overall stats
    if 'total_holdings' in data:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # Handle both dictionary and direct value formats
            if isinstance(data['total_holdings'], dict):
                total_eth = data['total_holdings'].get('ethereum', 0)
            else:
                total_eth = data['total_holdings']
            tracker.render_metric("Total ETH Held", f"{total_eth:,.0f} ETH", "metric-green")
        
        with col2:
            total_value = data.get('total_value_usd', 0)
            tracker.render_metric("Total Value", tracker.format_currency(total_value, currency), "metric-blue")
        
        with col3:
            total_companies = len(data.get('companies', []))
            avg_eth = (total_eth / total_companies) if total_companies else 0
            tracker.render_metric("Avg ETH / Company", f"{avg_eth:,.0f}", "metric-orange")
        
        with col4:
            tracker.render_metric("Companies Tracked", f"{total_companies}", "metric-purple")

        with col5:
            # Market cap dominance for ETH = sum of company supply percentages
            dominance = 0.0
            try:
                companies = data.get('companies', [])
                if companies:
                    dominance = sum([c.get('percentage_of_total_supply', 0) or 0 for c in companies])
            except Exception:
                dominance = 0.0
            tracker.render_metric("Market Cap Dominance", f"{dominance:.2f}%", "metric-teal")
    
    # Process data
    df = tracker.process_treasury_data(data, "ethereum")
    
    if not df.empty:
        # Display table
        st.subheader("🏢 Company Holdings")
        
        # Format display columns
        display_df = df.copy()
        display_df['Total Holdings'] = display_df['Total Holdings'].apply(lambda x: f"{x:,.0f}")
        display_df['Entry Value'] = display_df['Entry Value'].apply(lambda v: tracker.format_currency(v, currency))
        display_df['Current Value'] = display_df['Current Value'].apply(lambda v: tracker.format_currency(v, currency))
        display_df['PnL'] = display_df['PnL'].apply(lambda v: tracker.format_currency(v, currency))
        display_df['PnL %'] = display_df['PnL %'].apply(lambda x: f"{x:.2f}%")
        display_df['% of Total Supply'] = display_df['% of Total Supply'].apply(lambda x: f"{x:.3f}%")
        
        st.dataframe(display_df, use_container_width=True)

        # Charts row
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            # Donut: Companies vs Others share of ETH supply (from API percentages sum)
            companies_share = df['% of Total Supply'].sum() if '% of Total Supply' in df.columns else 0
            companies_share = max(0.0, min(100.0, companies_share))
            others_share = 100 - companies_share
            pie_fig = px.pie(values=[companies_share, others_share], names=['Public Companies', 'Others'], hole=0.6,
                              title='Share of ETH Supply (Companies vs Others)')
            pie_fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(pie_fig, use_container_width=True)
        with chart_col2:
            # Top companies by current value
            top_df = df.nlargest(10, 'Current Value')
            bar_fig = px.bar(top_df, x='Name', y='Current Value', title='Top Public Companies Holding ETH')
            bar_fig.update_yaxes(title_text=f"Value ({currency})")
            st.plotly_chart(bar_fig, use_container_width=True)

def display_combined_data(tracker, btc_data, eth_data, currency):
    """Display combined Bitcoin and Ethereum data"""
    st.header("📊 Combined Treasury Holdings")
    
    # Process both datasets
    btc_df = tracker.process_treasury_data(btc_data, "bitcoin") if btc_data else pd.DataFrame()
    eth_df = tracker.process_treasury_data(eth_data, "ethereum") if eth_data else pd.DataFrame()
    
    # Create combined view
    if not btc_df.empty or not eth_df.empty:
        # Normalize column names for merge
        for df in [btc_df, eth_df]:
            if not df.empty:
                df.rename(columns={
                    'Name': 'Company',
                    'Total Holdings': 'Holdings',
                    'Entry Value': 'EntryUSD',
                    'Current Value': 'CurrentUSD'
                }, inplace=True)
        btc_df['Asset'] = 'BTC' if not btc_df.empty else 'BTC'
        eth_df['Asset'] = 'ETH' if not eth_df.empty else 'ETH'

        # Merge outer on company identity
        combined_df = pd.merge(
            btc_df[['Company','Symbol','Country','Holdings','EntryUSD','CurrentUSD']].rename(columns={
                'Holdings':'BTC Held', 'EntryUSD':'EntryUSD_BTC', 'CurrentUSD':'CurrentUSD_BTC'
            }) if not btc_df.empty else pd.DataFrame(columns=['Company','Symbol','Country','BTC Held','EntryUSD_BTC','CurrentUSD_BTC']),
            eth_df[['Company','Symbol','Country','Holdings','EntryUSD','CurrentUSD']].rename(columns={
                'Holdings':'ETH Held', 'EntryUSD':'EntryUSD_ETH', 'CurrentUSD':'CurrentUSD_ETH'
            }) if not eth_df.empty else pd.DataFrame(columns=['Company','Symbol','Country','ETH Held','EntryUSD_ETH','CurrentUSD_ETH']),
            on=['Company','Symbol','Country'], how='outer'
        ).fillna(0)

        # Totals (USD basis)
        combined_df['Total Entry Value'] = combined_df.get('EntryUSD_BTC', 0) + combined_df.get('EntryUSD_ETH', 0)
        combined_df['Total Current Value'] = combined_df.get('CurrentUSD_BTC', 0) + combined_df.get('CurrentUSD_ETH', 0)
        combined_df['Total PnL'] = combined_df['Total Current Value'] - combined_df['Total Entry Value']

        # Metrics row 1
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            total_btc = combined_df['BTC Held'].sum() if 'BTC Held' in combined_df.columns else 0
            tracker.render_metric("Total BTC Held", f"{total_btc:,.0f} BTC", "metric-green")
        with m2:
            total_eth = combined_df['ETH Held'].sum() if 'ETH Held' in combined_df.columns else 0
            tracker.render_metric("Total ETH Held", f"{total_eth:,.0f} ETH", "metric-green")
        with m3:
            total_entry = float(combined_df['Total Entry Value'].sum())
            tracker.render_metric("Total Entry Value", tracker.format_currency(total_entry, currency), "metric-blue")
        with m4:
            total_current = float(combined_df['Total Current Value'].sum())
            tracker.render_metric("Total Current Value", tracker.format_currency(total_current, currency), "metric-blue")

        # Metrics row 2
        n1, n2, n3, n4 = st.columns(4)
        with n1:
            total_pnl = total_current - total_entry
            tracker.render_metric("Total PnL", tracker.format_currency(total_pnl, currency), "metric-orange")
        with n2:
            pnl_pct = (total_pnl / total_entry * 100) if total_entry > 0 else 0
            tracker.render_metric("Total PnL %", f"{pnl_pct:.2f}%", "metric-orange")
        with n3:
            total_companies = len(combined_df)
            tracker.render_metric("Total Companies", f"{total_companies}", "metric-purple")
        with n4:
            btc_companies = len(combined_df[combined_df['BTC Held'] > 0]) if 'BTC Held' in combined_df.columns else 0
            eth_companies = len(combined_df[combined_df['ETH Held'] > 0]) if 'ETH Held' in combined_df.columns else 0
            tracker.render_metric("BTC / ETH Companies", f"{btc_companies} / {eth_companies}", "metric-purple")

        # Display combined table
        st.subheader("🏢 Combined Company Holdings")
        
        # Format display columns
        display_df = combined_df.copy()
        if 'BTC Held' in display_df.columns:
            display_df['BTC Held'] = display_df['BTC Held'].apply(lambda x: tracker.format_crypto_amount(x, 'BTC'))
        if 'ETH Held' in display_df.columns:
            display_df['ETH Held'] = display_df['ETH Held'].apply(lambda x: tracker.format_crypto_amount(x, 'ETH'))
        display_df['EntryUSD_BTC'] = display_df.get('EntryUSD_BTC', 0)
        display_df['CurrentUSD_BTC'] = display_df.get('CurrentUSD_BTC', 0)
        display_df['EntryUSD_ETH'] = display_df.get('EntryUSD_ETH', 0)
        display_df['CurrentUSD_ETH'] = display_df.get('CurrentUSD_ETH', 0)
        display_df['Total Entry Value'] = display_df['Total Entry Value']
        display_df['Total Current Value'] = display_df['Total Current Value']
        display_df['Total PnL'] = display_df['Total PnL']

        # Derive per-company combined PnL
        display_df['Company PnL'] = (combined_df['Total Current Value'] - combined_df['Total Entry Value'])
        display_df['Company PnL %'] = combined_df.apply(
            lambda r: ((r['Total Current Value'] - r['Total Entry Value']) / r['Total Entry Value'] * 100) if r['Total Entry Value'] and r['Total Entry Value'] != 0 else 0,
            axis=1,
        )
        # Currency formatting for visible columns
        for col in ['EntryUSD_BTC','CurrentUSD_BTC','EntryUSD_ETH','CurrentUSD_ETH','Total Entry Value','Total Current Value','Total PnL','Company PnL']:
            display_df[col] = display_df[col].apply(lambda v: tracker.format_currency(v, currency))
        display_df['Company PnL %'] = display_df['Company PnL %'].apply(lambda x: f"{x:.2f}%")
        
        # Order columns if present
        preferred_cols = [
            'Company','Symbol','Country','BTC Held','EntryUSD_BTC','CurrentUSD_BTC','ETH Held','EntryUSD_ETH','CurrentUSD_ETH','Total Entry Value','Total Current Value','Total PnL','Company PnL','Company PnL %'
        ]
        existing_cols = [c for c in preferred_cols if c in display_df.columns]
        st.dataframe(display_df[existing_cols], use_container_width=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top companies by total value (Company on x-axis)
            top_10 = combined_df.nlargest(10, 'Total Current Value')
            fig = px.bar(
                top_10,
                x='Company',
                y='Total Current Value',
                title="Top 10 Companies by Total Value"
            )
            fig.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Asset distribution pie chart
            btc_total = combined_df['CurrentUSD_BTC'].sum() if 'CurrentUSD_BTC' in combined_df.columns else 0
            eth_total = combined_df['CurrentUSD_ETH'].sum() if 'CurrentUSD_ETH' in combined_df.columns else 0
            
            fig = px.pie(
                values=[btc_total, eth_total],
                names=['Bitcoin', 'Ethereum'],
                title="Asset Distribution by Value"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
