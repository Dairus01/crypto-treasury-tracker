#  Crypto Treasury Tracker

A comprehensive web application that tracks Bitcoin and Ethereum holdings of public companies with real-time PnL analysis, built with Streamlit and powered by CoinGecko API.

##  Features

### Core Functionality
- **Real-time Data**: Live treasury holdings data from CoinGecko API
- **Dual Asset Support**: Track both Bitcoin (BTC) and Ethereum (ETH) holdings
- **PnL Analysis**: Calculate profit/loss for each company's crypto investments
- **Company Details**: Company name, ticker, country, and holdings information

### Interactive Features
- **Asset Selection**: Switch between BTC, ETH, or view both simultaneously
- **Currency Conversion**: Support for multiple currencies (USD, EUR, GBP, JPY, CAD, AUD)
- **What-If Analysis**: Interactive scenario modeling with adjustable crypto prices
- **Real-time Charts**: Visual representation of holdings and PnL distribution

### Advanced Analytics
- **Top Holders Ranking**: Identify companies with largest crypto positions
- **PnL Distribution**: Histogram analysis of profit/loss across companies
- **Combined View**: Unified dashboard for companies holding both assets
- **Supply Percentage**: BTC holdings as percentage of total supply

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Data Processing**: Pandas for data manipulation
- **Visualization**: Plotly for interactive charts
- **API Integration**: CoinGecko Companies Treasury API
- **Caching**: Built-in caching for optimal performance

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for real-time data

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dairus01/crypto-treasury-tracker
   cd crypto-treasury-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```


## 🎯 Usage

### Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:8501`
   - The app will automatically load and fetch latest data

### Using the Interface

1. **Asset Selection**: Choose between Bitcoin, Ethereum, or both
2. **Currency**: Select your preferred display currency
3. **What-If Analysis**: Adjust crypto prices to see impact on holdings
4. **Data Refresh**: Click refresh button to get latest data
5. **Interactive Charts**: Hover over charts for detailed information

## 📊 Data Sources

- **CoinGecko Companies Treasury API**: Primary data source for company holdings
- **Real-time Pricing**: Current market values and exchange rates
- **Public Disclosures**: Company-reported crypto treasury positions


## 📈 Features in Detail

### Treasury Holdings Display
- Company name and stock ticker
- Country of incorporation
- Crypto holdings (BTC/ETH amount)
- Entry value (acquisition cost)
- Current market value
- Unrealized PnL (profit/loss)
- PnL percentage


### Visual Analytics
- **Bar Charts**: Top companies by holdings
- **Histograms**: PnL distribution analysis
- **Pie Charts**: Asset allocation breakdown
- **Interactive Tables**: Sortable company data

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy automatically


## 📊 Performance Optimization

- **Caching**: 1-hour cache for API responses
- **Lazy Loading**: Data fetched only when needed
- **Efficient Processing**: Pandas for fast data manipulation
- **Responsive UI**: Streamlit's optimized rendering

## 🎯 Use Cases

### For Investors
- Track corporate crypto adoption
- Analyze company crypto strategies
- Monitor institutional crypto exposure
- Identify crypto-friendly companies

### For Analysts
- Research crypto market trends
- Analyze corporate treasury strategies
- Monitor institutional adoption
- Generate investment insights

### For Companies
- Benchmark against competitors
- Track industry crypto adoption
- Analyze treasury diversification
- Monitor market positioning

## 🔮 Future Enhancements

- **Additional Assets**: Support for more cryptocurrencies
- **Historical Data**: Time-series analysis and trends
- **Private Companies**: Include non-public entities
- **Portfolio Tracking**: User-defined watchlists
- **Alerts**: Price and PnL notifications
- **Export Features**: CSV/Excel data export
- **Mobile App**: Native mobile application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License 

## ⚠️ Disclaimer

This application is for educational and informational purposes only. The data provided is sourced from public APIs and should not be considered as financial advice. Always conduct your own research before making investment decisions.

## 🆘 Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Check this README first
- **API Issues**: Contact CoinGecko support
- **Community**: Join our discussions

## 🏆 Acknowledgments

- **CoinGecko**: For providing the treasury data API
- **Streamlit**: For the excellent web app framework
- **Open Source Community**: For the amazing tools and libraries

---

**Built with ❤️ for the crypto community**

